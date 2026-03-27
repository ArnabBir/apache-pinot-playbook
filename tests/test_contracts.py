import json
from pathlib import Path

import jsonschema
import yaml

from pinot_playbook_demo.data_gen import generate_merchants, generate_trip_events


def test_contract_files_parse():
    assert yaml.safe_load(Path("contracts/openapi/analytics-api.yaml").read_text(encoding="utf-8"))
    assert yaml.safe_load(Path("contracts/asyncapi/trip-events.asyncapi.yaml").read_text(encoding="utf-8"))
    assert json.loads(Path("contracts/jsonschema/trip-event.schema.json").read_text(encoding="utf-8"))


def test_generated_events_match_json_schema():
    schema = json.loads(Path("contracts/jsonschema/trip-event.schema.json").read_text(encoding="utf-8"))
    merchants = generate_merchants(seed=42)
    events = generate_trip_events(seed=42, merchants=merchants)
    for event in events[:10]:
        jsonschema.validate(event.model_dump(mode="json"), schema)
