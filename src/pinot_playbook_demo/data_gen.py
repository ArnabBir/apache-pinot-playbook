from __future__ import annotations

import csv
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .models import (
    City,
    ContractTier,
    EventType,
    Merchant,
    PaymentMethod,
    ServiceTier,
    TripEvent,
    TripState,
    Vertical)


CITY_ZONES: Dict[City, List[str]] = {
    City.bengaluru: ["indiranagar", "koramangala", "whitefield", "hsr", "malleshwaram"],
    City.mumbai: ["powai", "bandra", "andheri", "worli", "thane"],
    City.delhi: ["saket", "dwarka", "cp", "rohini", "vasant_kunj"],
    City.hyderabad: ["gachibowli", "jubliee_hills", "hitech_city", "madhapur", "banjara_hills"],
    City.pune: ["baner", "wakad", "kothrud", "hinjewadi", "viman_nagar"],
    City.chennai: ["adyar", "omr", "anna_nagar", "velachery", "tambaram"],
}

MERCHANT_NAME_PREFIX = {
    Vertical.restaurant: ["Spice Route", "Tandoor House", "Urban Tiffin", "Metro Meals"],
    Vertical.grocery: ["Daily Basket", "Fresh Cart", "Quick Mart", "Green Crate"],
    Vertical.pharmacy: ["Care Chemist", "Health Shelf", "MediSprint", "City Rx"],
    Vertical.electronics: ["Circuit Corner", "Nano Plaza", "Signal Store", "Volt Vault"],
    Vertical.fashion: ["Thread & Tone", "Metro Loom", "Label Lane", "Street Stitch"],
}


def stable_hash(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)


def fake_h3(city: City, zone: str, salt: str) -> str:
    seed = stable_hash(f"{city}:{zone}:{salt}")
    return f"8{seed:014x}"[:15]


def truncate_bucket_ms(epoch_ms: int, bucket_minutes: int = 5) -> int:
    bucket_ms = bucket_minutes * 60 * 1000
    return epoch_ms - (epoch_ms % bucket_ms)


def generate_merchants(n: int = 36, seed: int = 42) -> List[Merchant]:
    rng = random.Random(seed)
    cities = list(City)
    verticals = list(Vertical)
    contract_tiers = list(ContractTier)
    merchants: List[Merchant] = []
    base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

    for idx in range(n):
        city = cities[idx % len(cities)]
        vertical = verticals[idx % len(verticals)]
        contract = contract_tiers[idx % len(contract_tiers)]
        name_prefix = MERCHANT_NAME_PREFIX[vertical][idx % len(MERCHANT_NAME_PREFIX[vertical])]
        merchants.append(
            Merchant(
                merchant_id=f"m_{idx + 1:03d}",
                merchant_name=f"{name_prefix} {city.value.title()} {idx % 9 + 1}",
                city=city,
                vertical=vertical,
                contract_tier=contract,
                rating=round(rng.uniform(3.7, 4.9), 2),
                is_active=rng.random() > 0.05,
                monthly_orders=rng.randint(1_000, 50_000),
                onboarding_date=(base_date + timedelta(days=idx * 7)).date().isoformat())
        )
    return merchants


def pick_status(event_type: EventType) -> str:
    return {
        EventType.created: "searching",
        EventType.accepted: "driver_assigned",
        EventType.en_route: "driver_en_route",
        EventType.picked_up: "in_transit",
        EventType.completed: "completed",
        EventType.cancelled: "cancelled",
        EventType.deleted: "deleted",
    }[event_type]


def generate_trip_events(
    n_trips: int = 400,
    max_updates: int = 5,
    seed: int = 42,
    merchants: Sequence[Merchant] | None = None) -> List[TripEvent]:
    rng = random.Random(seed)
    merchants = list(merchants or generate_merchants(seed=seed))
    merchants_by_city: Dict[City, List[Merchant]] = defaultdict(list)
    for merchant in merchants:
        merchants_by_city[merchant.city].append(merchant)
    events: List[TripEvent] = []
    lifecycle_templates: List[List[EventType]] = [
        [EventType.created, EventType.accepted, EventType.en_route, EventType.picked_up, EventType.completed],
        [EventType.created, EventType.accepted, EventType.cancelled],
        [EventType.created, EventType.accepted, EventType.en_route, EventType.cancelled],
        [EventType.created, EventType.accepted, EventType.picked_up, EventType.completed],
    ]

    base_dt = datetime(2024, 1, 1, tzinfo=timezone.utc)

    for idx in range(n_trips):
        city = list(City)[idx % len(City)]
        merchant = rng.choice(merchants_by_city[city])
        sequence = list(rng.choice(lifecycle_templates))[:max_updates]
        trip_id = f"trip_{idx + 1:06d}"
        driver_id = f"drv_{stable_hash(trip_id) % 3500:05d}"
        rider_id = f"rdr_{stable_hash(trip_id[::-1]) % 10000:05d}"
        service_tier = rng.choices(
            population=[ServiceTier.economy, ServiceTier.premium, ServiceTier.xl],
            weights=[0.7, 0.2, 0.1],
            k=1)[0]
        payment_method = rng.choice(list(PaymentMethod))
        pickup_zone = rng.choice(CITY_ZONES[city])
        dropoff_zone = rng.choice(CITY_ZONES[city])
        distance_km = round(rng.uniform(1.2, 18.0), 2)
        eta_seconds = rng.randint(420, 3600)
        base_fare = round(35 + distance_km * rng.uniform(8.5, 17.5), 2)
        surge_multiplier = round(rng.choice([1.0, 1.0, 1.1, 1.2, 1.5, 1.8]), 2)
        first_offset_minutes = rng.randint(0, 14 * 24 * 60)
        current_dt = base_dt + timedelta(minutes=first_offset_minutes)

        for version, event_type in enumerate(sequence, start=1):
            current_dt += timedelta(minutes=rng.randint(2, 14))
            event_ms = int(current_dt.timestamp() * 1000)
            if event_type == EventType.cancelled:
                fare = 0.0
            elif event_type in (EventType.created, EventType.accepted, EventType.en_route):
                fare = round(base_fare * 0.0, 2)
            else:
                fare = round(base_fare * surge_multiplier, 2)

            attributes = {
                "source": "simulator",
                "merchant_vertical_hint": merchant.vertical.value,
                "coupon_applied": rng.random() < 0.18,
                "traffic_index": round(rng.uniform(0.6, 2.2), 2),
                "weather": rng.choice(["clear", "cloudy", "rain", "fog"]),
            }

            events.append(
                TripEvent(
                    trip_id=trip_id,
                    merchant_id=merchant.merchant_id,
                    merchant_name=merchant.merchant_name,
                    driver_id=driver_id,
                    rider_id=rider_id,
                    city=city,
                    service_tier=service_tier,
                    event_type=event_type,
                    status=pick_status(event_type),
                    payment_method=payment_method,
                    event_time_ms=event_ms,
                    event_day=current_dt.date().isoformat(),
                    event_hour=current_dt.hour,
                    event_minute_bucket_ms=truncate_bucket_ms(event_ms, 5),
                    trip_partition=stable_hash(trip_id) % 16,
                    pickup_zone=pickup_zone,
                    dropoff_zone=dropoff_zone,
                    pickup_h3=fake_h3(city, pickup_zone, trip_id),
                    dropoff_h3=fake_h3(city, dropoff_zone, trip_id[::-1]),
                    fare_amount=fare,
                    distance_km=distance_km,
                    eta_seconds=eta_seconds,
                    surge_multiplier=surge_multiplier,
                    event_version=version,
                    is_deleted=False,
                    attributes=attributes)
            )

        if rng.random() < 0.03:
            current_dt += timedelta(minutes=rng.randint(5, 120))
            event_ms = int(current_dt.timestamp() * 1000)
            events.append(
                TripEvent(
                    trip_id=trip_id,
                    merchant_id=merchant.merchant_id,
                    merchant_name=merchant.merchant_name,
                    driver_id=driver_id,
                    rider_id=rider_id,
                    city=city,
                    service_tier=service_tier,
                    event_type=EventType.deleted,
                    status=pick_status(EventType.deleted),
                    payment_method=payment_method,
                    event_time_ms=event_ms,
                    event_day=current_dt.date().isoformat(),
                    event_hour=current_dt.hour,
                    event_minute_bucket_ms=truncate_bucket_ms(event_ms, 5),
                    trip_partition=stable_hash(trip_id) % 16,
                    pickup_zone=pickup_zone,
                    dropoff_zone=dropoff_zone,
                    pickup_h3=fake_h3(city, pickup_zone, trip_id),
                    dropoff_h3=fake_h3(city, dropoff_zone, trip_id[::-1]),
                    fare_amount=0.0,
                    distance_km=distance_km,
                    eta_seconds=eta_seconds,
                    surge_multiplier=surge_multiplier,
                    event_version=len(sequence) + 1,
                    is_deleted=True,
                    attributes={"source": "simulator", "reason": "gdpr_erasure"})
            )

    events.sort(key=lambda e: (e.event_time_ms, e.trip_id, e.event_version))
    return events


def derive_trip_states(events: Sequence[TripEvent]) -> List[TripState]:
    latest: Dict[str, TripEvent] = {}
    for event in events:
        prev = latest.get(event.trip_id)
        if prev is None or (event.event_version, event.event_time_ms) > (prev.event_version, prev.event_time_ms):
            latest[event.trip_id] = event

    states = [
        TripState(
            trip_id=event.trip_id,
            merchant_id=event.merchant_id,
            merchant_name=event.merchant_name,
            driver_id=event.driver_id,
            rider_id=event.rider_id,
            city=event.city,
            service_tier=event.service_tier,
            status=event.status,
            payment_method=event.payment_method,
            last_event_type=event.event_type,
            last_event_time_ms=event.event_time_ms,
            last_event_day=event.event_day,
            last_event_hour=event.event_hour,
            last_event_minute_bucket_ms=event.event_minute_bucket_ms,
            trip_partition=event.trip_partition,
            fare_amount=event.fare_amount,
            distance_km=event.distance_km,
            eta_seconds=event.eta_seconds,
            surge_multiplier=event.surge_multiplier,
            event_version=event.event_version,
            is_deleted=event.is_deleted,
            attributes=event.attributes)
        for event in latest.values()
    ]
    states.sort(key=lambda s: (s.last_event_time_ms, s.trip_id))
    return states


def write_jsonl(records: Iterable[dict], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def write_csv_rows(rows: Iterable[dict], output_path: str | Path, fieldnames: Sequence[str]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def write_kafka_lines(records: Iterable[dict], key_field: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in records:
            key = record[key_field]
            # Pinot STRING columns can't hold JSON objects, so stringify nested types
            serializable = {}
            for k, v in record.items():
                if isinstance(v, (dict, list)):
                    serializable[k] = json.dumps(v, ensure_ascii=False)
                else:
                    serializable[k] = v
            f.write(f"{key}|{json.dumps(serializable, ensure_ascii=False)}\n")
    return path


def merchants_to_rows(merchants: Sequence[Merchant]) -> List[dict]:
    return [merchant.model_dump(mode="json") for merchant in merchants]


def events_to_rows(events: Sequence[TripEvent]) -> List[dict]:
    return [event.model_dump(mode="json") for event in events]


def states_to_rows(states: Sequence[TripState]) -> List[dict]:
    return [state.model_dump(mode="json") for state in states]
