#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(repo_root))

import yaml

from app.main import app
from pinot_playbook_demo.models import TripEvent


def main() -> None:
    base = Path("contracts")
    (base / "openapi").mkdir(parents=True, exist_ok=True)
    (base / "jsonschema").mkdir(parents=True, exist_ok=True)
    (base / "examples").mkdir(parents=True, exist_ok=True)

    openapi_path = base / "openapi" / "analytics-api.yaml"
    schema_path = base / "jsonschema" / "trip-event.schema.json"

    openapi = app.openapi()
    openapi_path.write_text(yaml.safe_dump(openapi, sort_keys=False), encoding="utf-8")

    schema = TripEvent.model_json_schema()
    schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")

    example = {
        "trip_id": "trip_000001",
        "merchant_id": "m_001",
        "merchant_name": "Spice Route Bengaluru 1",
        "driver_id": "drv_00001",
        "rider_id": "rdr_00001",
        "city": "bengaluru",
        "service_tier": "economy",
        "event_type": "completed",
        "status": "completed",
        "payment_method": "upi",
        "event_time_ms": 1767225600000,
        "event_day": "2026-01-01",
        "event_hour": 10,
        "event_minute_bucket_ms": 1767225600000,
        "trip_partition": 5,
        "pickup_zone": "koramangala",
        "dropoff_zone": "whitefield",
        "pickup_h3": "8f6a8b0c0d0e0f",
        "dropoff_h3": "8f6a8b0c0d0e10",
        "fare_amount": 187.5,
        "distance_km": 8.2,
        "eta_seconds": 900,
        "surge_multiplier": 1.5,
        "event_version": 5,
        "is_deleted": False,
        "attributes": {"source": "simulator"}
    }
    (base / "examples" / "trip-event.example.json").write_text(json.dumps(example, indent=2), encoding="utf-8")
    print(f"Wrote {openapi_path} and {schema_path}")


if __name__ == "__main__":
    main()
