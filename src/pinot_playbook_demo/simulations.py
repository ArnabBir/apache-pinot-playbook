from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .data_gen import derive_trip_states
from .models import TripEvent


def simulate_segment_pruning(
    events: Sequence[TripEvent],
    city_filter: Optional[str],
    start_ms: int,
    end_ms: int,
    segment_minutes: int = 60) -> Dict[str, Any]:
    segment_ms = segment_minutes * 60 * 1000
    segments: Dict[Tuple[int, str], List[TripEvent]] = defaultdict(list)
    for event in events:
        bucket = event.event_time_ms - (event.event_time_ms % segment_ms)
        segments[(bucket, event.city.value)].append(event)

    all_segments = list(segments.items())
    total_rows = sum(len(rows) for _, rows in all_segments)
    scanned_without_pruning = total_rows

    time_pruned_segments = [rows for (bucket, _city), rows in all_segments if start_ms <= bucket <= end_ms]
    rows_with_time_pruning = sum(len(rows) for rows in time_pruned_segments)

    fully_pruned_segments = [
        rows for (bucket, city), rows in all_segments
        if start_ms <= bucket <= end_ms and (city_filter is None or city == city_filter)
    ]
    rows_with_time_and_city_pruning = sum(len(rows) for rows in fully_pruned_segments)

    return {
        "segment_minutes": segment_minutes,
        "total_segments": len(all_segments),
        "scanned_rows_without_pruning": scanned_without_pruning,
        "scanned_rows_with_time_pruning": rows_with_time_pruning,
        "scanned_rows_with_time_and_city_pruning": rows_with_time_and_city_pruning,
        "time_pruning_gain_pct": round(100 * (1 - rows_with_time_pruning / max(scanned_without_pruning, 1)), 2),
        "full_pruning_gain_pct": round(100 * (1 - rows_with_time_and_city_pruning / max(scanned_without_pruning, 1)), 2),
    }


def simulate_star_tree(
    events: Sequence[TripEvent],
    dimensions: Tuple[str, str] = ("city", "service_tier")) -> Dict[str, Any]:
    aggregate_map: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(lambda: {"count": 0, "gmv": 0.0})
    for event in events:
        key = (getattr(event.city, "value", str(event.city)), getattr(event.service_tier, "value", str(event.service_tier)))
        bucket = aggregate_map[key]
        bucket["count"] += 1
        bucket["gmv"] += event.fare_amount

    raw_rows = len(events)
    aggregate_cells = len(aggregate_map)
    compression_ratio = round(raw_rows / max(aggregate_cells, 1), 2)

    top_groups = sorted(
        ((city, tier, values["count"], round(values["gmv"], 2)) for (city, tier), values in aggregate_map.items()),
        key=lambda x: (-x[3], -x[2], x[0], x[1]))[:10]

    return {
        "dimensions": list(dimensions),
        "raw_rows": raw_rows,
        "aggregate_cells": aggregate_cells,
        "compression_ratio": compression_ratio,
        "top_groups": top_groups,
    }


def simulate_upsert(events: Sequence[TripEvent]) -> Dict[str, Any]:
    latest = {}
    stale_events = 0
    delete_events = 0
    version_histogram = Counter()

    for event in events:
        version_histogram[event.event_version] += 1
        existing = latest.get(event.trip_id)
        if existing and (event.event_version, event.event_time_ms) <= (existing.event_version, existing.event_time_ms):
            stale_events += 1
            continue
        latest[event.trip_id] = event
        if event.is_deleted:
            delete_events += 1

    states = derive_trip_states(events)
    active_states = [state for state in states if not state.is_deleted]
    deleted_states = [state for state in states if state.is_deleted]

    return {
        "input_event_rows": len(events),
        "distinct_trip_ids": len({event.trip_id for event in events}),
        "latest_state_rows": len(states),
        "active_state_rows": len(active_states),
        "deleted_state_rows": len(deleted_states),
        "stale_events_dropped": stale_events,
        "delete_events_seen": delete_events,
        "event_version_histogram": dict(sorted(version_histogram.items())),
    }


def simulate_partition_skew(events: Sequence[TripEvent], partitions: int = 16) -> Dict[str, Any]:
    buckets = Counter(event.trip_partition % partitions for event in events)
    max_count = max(buckets.values()) if buckets else 0
    min_count = min(buckets.values()) if buckets else 0
    avg = sum(buckets.values()) / max(len(buckets), 1)
    skew_ratio = round(max_count / max(avg, 1), 2)
    return {
        "partitions": partitions,
        "distribution": dict(sorted(buckets.items())),
        "max_partition_rows": max_count,
        "min_partition_rows": min_count,
        "skew_ratio": skew_ratio,
    }
