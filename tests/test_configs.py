import json
from pathlib import Path

import yaml


def test_summary_references_exist():
    content = Path("SUMMARY.md").read_text(encoding="utf-8").splitlines()
    links = [line.split("](")[1].rstrip(")") for line in content if "](" in line]
    for link in links:
        assert Path(link).exists(), f"Missing SUMMARY link target: {link}"


def test_schema_and_table_json_parse():
    for folder in ("schemas", "tables"):
        for path in Path(folder).glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert data


def test_job_spec_and_asyncapi_parse():
    assert yaml.safe_load(Path("jobs/merchants.job.yml").read_text(encoding="utf-8"))
    assert yaml.safe_load(Path("contracts/asyncapi/trip-events.asyncapi.yaml").read_text(encoding="utf-8"))
