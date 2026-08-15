from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Tuple, Union

from .data_gen import derive_trip_states, events_to_rows, generate_merchants, generate_trip_events, merchants_to_rows, states_to_rows
from .models import City, KPIResponse, MerchantStats, SQLRequest, TimeSeriesPoint, TimeSeriesRequest
from .pinot_client import PinotBrokerClient, extract_result_rows


def load_sample_data(base_dir: Optional[Union[str, Path]] = None) -> Tuple[List[dict], List[dict], List[dict]]:
    base = Path(base_dir or Path(__file__).resolve().parents[2] / "data")
    events_file = base / "sample_trip_events.jsonl"
    state_file = base / "sample_trip_state.jsonl"
    merchants_file = base / "merchants.csv"

    if events_file.exists() and state_file.exists():
        events = [json.loads(line) for line in events_file.read_text(encoding="utf-8").splitlines() if line.strip()]
        states = [json.loads(line) for line in state_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        merchants_models = generate_merchants()
        events_models = generate_trip_events(merchants=merchants_models)
        states_models = derive_trip_states(events_models)
        events = events_to_rows(events_models)
        states = states_to_rows(states_models)

    if merchants_file.exists():
        import csv
        with merchants_file.open("r", encoding="utf-8") as f:
            merchants = list(csv.DictReader(f))
            # normalize types
            for merchant in merchants:
                merchant["rating"] = float(merchant["rating"])
                merchant["monthly_orders"] = int(merchant["monthly_orders"])
                merchant["is_active"] = merchant["is_active"] in ("True", "true", True)
    else:
        merchants = merchants_to_rows(generate_merchants())
    return events, states, merchants


class AnalyticsProvider(Protocol):
    mode: str

    def is_available(self) -> bool: ...
    def health(self) -> Dict[str, Any]: ...
    def get_kpis(self, city: Optional[str], window_minutes: int) -> KPIResponse: ...
    def top_merchants(self, city: Optional[str], limit: int) -> List[MerchantStats]: ...
    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]: ...
    def sql(self, request: SQLRequest) -> Dict[str, Any]: ...
    def timeseries(self, request: TimeSeriesRequest) -> List[TimeSeriesPoint]: ...


class InMemoryAnalyticsProvider:
    mode = "sample"

    def __init__(self) -> None:
        self.events, self.states, self.merchants = load_sample_data()
        self.merchant_lookup = {m["merchant_id"]: m for m in self.merchants}
        self.state_lookup = {s["trip_id"]: s for s in self.states}
        self.generated_rows = len(self.events)

    def is_available(self) -> bool:
        return True

    def health(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "pinot_available": False,
            "generated_rows": self.generated_rows,
        }

    def _filter_states(self, city: Optional[str] = None) -> List[Dict[str, Any]]:
        rows = [state for state in self.states if not state.get("is_deleted")]
        if city:
            rows = [row for row in rows if row["city"] == city]
        return rows

    def _filter_recent_states(self, city: Optional[str], window_minutes: int) -> List[Dict[str, Any]]:
        rows = self._filter_states(city)
        if not rows:
            return rows
        max_ts = max(row["last_event_time_ms"] for row in rows)
        min_ts = max_ts - window_minutes * 60 * 1000
        return [row for row in rows if row["last_event_time_ms"] >= min_ts]

    def get_kpis(self, city: Optional[str], window_minutes: int) -> KPIResponse:
        rows = self._filter_recent_states(city, window_minutes)
        completed = [row for row in rows if row["status"] == "completed"]
        cancelled = [row for row in rows if row["status"] == "cancelled"]
        completed_fares = [float(row["fare_amount"]) for row in completed]
        distances = [float(row["distance_km"]) for row in completed]
        etas = [float(row["eta_seconds"]) for row in rows]
        return KPIResponse(
            city=City(city) if city else None,
            window_minutes=window_minutes,
            completed_trips=len(completed),
            cancelled_trips=len(cancelled),
            gross_merchandise_value=round(sum(completed_fares), 2),
            average_fare=round(sum(completed_fares) / max(len(completed_fares), 1), 2),
            average_distance_km=round(sum(distances) / max(len(distances), 1), 2),
            average_eta_seconds=round(sum(etas) / max(len(etas), 1), 2))

    def top_merchants(self, city: Optional[str], limit: int) -> List[MerchantStats]:
        rows = [row for row in self._filter_states(city) if row["status"] == "completed"]
        buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"completed_trips": 0, "revenue": 0.0})
        for row in rows:
            bucket = buckets[row["merchant_id"]]
            bucket["completed_trips"] += 1
            bucket["revenue"] += float(row["fare_amount"])

        ordered = sorted(
            buckets.items(),
            key=lambda kv: (-kv[1]["revenue"], -kv[1]["completed_trips"], kv[0]))[:limit]

        return [
            MerchantStats(
                merchant_id=merchant_id,
                merchant_name=self.merchant_lookup.get(merchant_id, {}).get("merchant_name", merchant_id),
                city=City(self.merchant_lookup.get(merchant_id, {}).get("city", city or "bengaluru")),
                completed_trips=stats["completed_trips"],
                revenue=round(stats["revenue"], 2))
            for merchant_id, stats in ordered
        ]

    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]:
        return self.state_lookup.get(trip_id)

    def _sql_count(self, rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        rows = list(rows)
        return {
            "resultTable": {
                "dataSchema": {"columnNames": ["count"], "columnDataTypes": ["LONG"]},
                "rows": [[len(rows)]],
            }
        }

    def sql(self, request: SQLRequest) -> Dict[str, Any]:
        query = " ".join(request.query.strip().split())
        lower = query.lower()

        city_match = re.search(r"where\s+city\s*=\s*'([^']+)'", lower)
        city = city_match.group(1) if city_match else None

        if re.fullmatch(r"select count\(\*\) from trip_events(?: where city = '[^']+')?;?", lower):
            rows = [row for row in self.events if not city or row["city"] == city]
            return self._sql_count(rows)

        if re.fullmatch(r"select count\(\*\) from trip_state(?: where city = '[^']+')?;?", lower):
            rows = [row for row in self.states if not city or row["city"] == city]
            return self._sql_count(rows)

        if "from trip_events" in lower and "group by city" in lower and "count(*)" in lower:
            filtered = [row for row in self.events if not city or row["city"] == city]
            counts = Counter(row["city"] for row in filtered)
            ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            return {
                "resultTable": {
                    "dataSchema": {
                        "columnNames": ["city", "event_count"],
                        "columnDataTypes": ["STRING", "LONG"],
                    },
                    "rows": [[city_name, count] for city_name, count in ordered],
                }
            }

        trip_match = re.search(r"where\s+trip_id\s*=\s*'([^']+)'", query, flags=re.IGNORECASE)
        if "from trip_state" in lower and trip_match:
            trip = self.get_trip(trip_match.group(1))
            if not trip:
                rows = []
                column_names = []
            else:
                column_names = list(trip.keys())
                rows = [[trip[name] for name in column_names]]
            return {
                "resultTable": {
                    "dataSchema": {"columnNames": column_names, "columnDataTypes": ["STRING"] * len(column_names)},
                    "rows": rows,
                }
            }

        if "from trip_state" in lower and "group by city" in lower and "sum(fare_amount)" in lower:
            rows = [row for row in self.states if row["status"] == "completed" and not row.get("is_deleted")]
            if city:
                rows = [row for row in rows if row["city"] == city]
            buckets: Dict[str, Dict[str, float]] = defaultdict(lambda: {"completed_trips": 0, "gmv": 0.0})
            for row in rows:
                bucket = buckets[row["city"]]
                bucket["completed_trips"] += 1
                bucket["gmv"] += float(row["fare_amount"])
            ordered = sorted(buckets.items(), key=lambda kv: (-kv[1]["gmv"], kv[0]))
            return {
                "resultTable": {
                    "dataSchema": {
                        "columnNames": ["city", "completed_trips", "gmv"],
                        "columnDataTypes": ["STRING", "LONG", "DOUBLE"],
                    },
                    "rows": [[k, int(v["completed_trips"]), round(v["gmv"], 2)] for k, v in ordered],
                }
            }

        return {
            "resultTable": {
                "dataSchema": {"columnNames": ["note"], "columnDataTypes": ["STRING"]},
                "rows": [[
                    "The in-memory provider supports COUNT(*), city group-bys, GMV by city and trip lookups. Use Pinot for full SQL semantics."
                ]],
            }
        }

    def timeseries(self, request: TimeSeriesRequest) -> List[TimeSeriesPoint]:
        rows = [row for row in self.states if not row.get("is_deleted")]
        if request.city:
            rows = [row for row in rows if row["city"] == request.city]
        if not rows:
            return []

        max_ts = max(row["last_event_time_ms"] for row in rows)
        min_ts = max_ts - request.window_hours * 60 * 60 * 1000
        rows = [row for row in rows if row["last_event_time_ms"] >= min_ts]

        bucket_ms = request.bucket_minutes * 60 * 1000
        buckets: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        for row in rows:
            start = row["last_event_time_ms"] - (row["last_event_time_ms"] % bucket_ms)
            buckets[start].append(row)

        points: list[TimeSeriesPoint] = []
        for start in sorted(buckets):
            batch = buckets[start]
            if request.metric == "gross_merchandise_value":
                value = sum(float(r["fare_amount"]) for r in batch if r["status"] == "completed")
            elif request.metric == "completed_trips":
                value = sum(1 for r in batch if r["status"] == "completed")
            else:
                etas = [float(r["eta_seconds"]) for r in batch]
                value = sum(etas) / max(len(etas), 1)
            points.append(TimeSeriesPoint(bucket_start_ms=start, value=round(float(value), 2)))
        return points


class PinotAnalyticsProvider:
    mode = "pinot"

    def __init__(self, broker_url: str | None = None) -> None:
        self.broker = PinotBrokerClient(base_url=broker_url or os.getenv("PINOT_BROKER_URL", "http://localhost:8099"))
        self.events_table = os.getenv("PINOT_EVENTS_TABLE", "trip_events")
        self.state_table = os.getenv("PINOT_STATE_TABLE", "trip_state")
        self.merchants_table = os.getenv("PINOT_MERCHANTS_TABLE", "merchants_dim")

    def is_available(self) -> bool:
        return self.broker.health()

    def health(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "pinot_available": self.is_available(),
            "generated_rows": 0,
        }

    def _scalar(self, query: str) -> float:
        result = self.broker.query_sql(query)
        rows = extract_result_rows(result)
        if not rows:
            return 0.0
        val = next(iter(rows[0].values()))
        if val is None or val == "" or val == "-Infinity" or val == "Infinity":
            return 0.0
        return float(val)

    def get_kpis(self, city: Optional[str], window_minutes: int) -> KPIResponse:
        latest_ts = int(self._scalar(f"SELECT MAX(last_event_time_ms) AS latest_ts FROM {self.state_table}"))
        min_ts = max(latest_ts - window_minutes * 60 * 1000, 0)
        filters = [f"last_event_time_ms >= {min_ts}"]
        if city:
            filters.append(f"city = '{city}'")
        where = " AND ".join(filters)
        completed_trips = int(self._scalar(
            f"SELECT COUNT(*) AS count FROM {self.state_table} WHERE status = 'completed' AND {where}"
        ))
        cancelled_trips = int(self._scalar(
            f"SELECT COUNT(*) AS count FROM {self.state_table} WHERE status = 'cancelled' AND {where}"
        ))
        gmv = self._scalar(
            f"SELECT SUM(fare_amount) AS total FROM {self.state_table} WHERE status = 'completed' AND {where}"
        )
        avg_fare = self._scalar(
            f"SELECT AVG(fare_amount) AS avg_fare FROM {self.state_table} WHERE status = 'completed' AND {where}"
        )
        avg_distance = self._scalar(
            f"SELECT AVG(distance_km) AS avg_distance FROM {self.state_table} WHERE status = 'completed' AND {where}"
        )
        avg_eta = self._scalar(
            f"SELECT AVG(eta_seconds) AS avg_eta FROM {self.state_table} WHERE status IN ('completed', 'cancelled') AND {where}"
        )
        return KPIResponse(
            city=City(city) if city else None,
            window_minutes=window_minutes,
            completed_trips=completed_trips,
            cancelled_trips=cancelled_trips,
            gross_merchandise_value=round(gmv, 2),
            average_fare=round(avg_fare, 2),
            average_distance_km=round(avg_distance, 2),
            average_eta_seconds=round(avg_eta, 2))

    def top_merchants(self, city: Optional[str], limit: int) -> List[MerchantStats]:
        where = "WHERE status = 'completed'"
        if city:
            where += f" AND city = '{city}'"
        query = f"""
        SELECT merchant_id, merchant_name, city, COUNT(*) AS completed_trips, SUM(fare_amount) AS revenue
        FROM {self.state_table}
        {where}
        GROUP BY merchant_id, merchant_name, city
        ORDER BY revenue DESC
        LIMIT {limit}
        """
        rows = extract_result_rows(self.broker.query_sql(query))
        return [
            MerchantStats(
                merchant_id=row["merchant_id"],
                merchant_name=row["merchant_name"],
                city=City(row["city"]),
                completed_trips=int(row["completed_trips"]),
                revenue=round(float(row["revenue"]), 2))
            for row in rows
        ]

    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {self.state_table} WHERE trip_id = '{trip_id}' LIMIT 1"
        rows = extract_result_rows(self.broker.query_sql(query))
        return rows[0] if rows else None

    def sql(self, request: SQLRequest) -> Dict[str, Any]:
        if request.query_type == "multistage":
            return self.broker.query_multistage(request.query, request.query_options)
        return self.broker.query_sql(request.query, request.query_options)

    def timeseries(self, request: TimeSeriesRequest) -> List[TimeSeriesPoint]:
        where = []
        if request.city:
            where.append(f"city = '{request.city}'")
        if request.metric == "completed_trips":
            where.append("status = 'completed'")
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        agg_expr = (
            "SUM(fare_amount)" if request.metric == "gross_merchandise_value"
            else "COUNT(*)" if request.metric == "completed_trips"
            else "AVG(eta_seconds)"
        )
        bucket_expr = (
            "DATETIMECONVERT(last_event_time_ms, '1:MILLISECONDS:EPOCH', "
            f"'1:MILLISECONDS:EPOCH', '{request.bucket_minutes}:MINUTES')"
        )
        query = f"""
        SELECT {bucket_expr} AS bucket_start_ms,
               {agg_expr} AS value
        FROM {self.state_table}
        {where_sql}
        GROUP BY {bucket_expr}
        ORDER BY bucket_start_ms
        """
        rows = extract_result_rows(self.broker.query_sql(query))
        return [TimeSeriesPoint(bucket_start_ms=int(r["bucket_start_ms"]), value=round(float(r["value"]), 2)) for r in rows]


def build_provider(mode: Optional[str] = None) -> AnalyticsProvider:
    mode = (mode or os.getenv("PINOT_MODE", "auto")).lower()

    if mode == "sample":
        return InMemoryAnalyticsProvider()
    if mode == "pinot":
        provider = PinotAnalyticsProvider()
        if not provider.is_available():
            raise RuntimeError("PINOT_MODE=pinot was requested but the Pinot broker is unreachable.")
        return provider

    pinot_provider = PinotAnalyticsProvider()
    if pinot_provider.is_available():
        return pinot_provider
    return InMemoryAnalyticsProvider()
