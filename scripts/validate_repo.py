#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

import jsonschema
import yaml

from pinot_playbook_demo.data_gen import derive_trip_states, generate_merchants, generate_trip_events
from pinot_playbook_demo.simulations import simulate_segment_pruning, simulate_star_tree, simulate_upsert


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    required_paths = [
        Path("README.md"),
        Path("SUMMARY.md"),
        Path("docker-compose.yml"),
        Path("contracts/openapi/analytics-api.yaml"),
        Path("contracts/jsonschema/trip-event.schema.json"),
        Path("schemas/trip_events.schema.json"),
        Path("tables/trip_events_rt.table.json"),
        Path("tables/trip_state_rt.table.json"),
        Path("tables/merchants_dim_offline.table.json"),
    ]
    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(path)

    # Parse YAML / JSON files
    yaml.safe_load(Path("contracts/openapi/analytics-api.yaml").read_text(encoding="utf-8"))
    yaml.safe_load(Path("contracts/asyncapi/trip-events.asyncapi.yaml").read_text(encoding="utf-8"))
    yaml.safe_load(Path("jobs/merchants.job.yml").read_text(encoding="utf-8"))
    for path in Path("schemas").glob("*.json"):
        load_json(path)
    for path in Path("tables").glob("*.json"):
        load_json(path)

    # Validate generated records against JSON Schema
    schema = load_json(Path("contracts/jsonschema/trip-event.schema.json"))
    merchants = generate_merchants()
    events = generate_trip_events(merchants=merchants)
    for event in events[:25]:
        jsonschema.validate(instance=event.model_dump(mode="json"), schema=schema)

    states = derive_trip_states(events)
    assert states, "No states derived"
    start_ms = min(event.event_time_ms for event in events)
    pruning = simulate_segment_pruning(events, city_filter="bengaluru", start_ms=start_ms, end_ms=start_ms + 3_600_000)
    assert pruning["scanned_rows_with_time_and_city_pruning"] <= pruning["scanned_rows_without_pruning"]

    star_tree = simulate_star_tree(events)
    assert star_tree["aggregate_cells"] < star_tree["raw_rows"]

    upsert = simulate_upsert(events)
    assert upsert["latest_state_rows"] <= upsert["input_event_rows"]

    print("Repository validation completed successfully.")


if __name__ == "__main__":
    main()
