from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


class PinotError(RuntimeError):
    pass


def _raise_for_error(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = response.text[:2_000]
        raise PinotError(f"Pinot API error {response.status_code}: {detail}") from exc


@dataclass
class PinotControllerClient:
    base_url: str = "http://localhost:9000"
    timeout: int = 20

    def health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url.rstrip('/')}/health", timeout=self.timeout)
            return response.ok
        except requests.RequestException:
            return False

    def create_schema(self, schema_path: str | Path) -> Dict[str, Any]:
        schema_path = Path(schema_path)
        with schema_path.open("rb") as f:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/schemas",
                files={"schemaName": (schema_path.name, f, "application/json")},
                timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def create_table(self, table_path: str | Path) -> Dict[str, Any]:
        table_path = Path(table_path)
        payload = json.loads(table_path.read_text(encoding="utf-8"))
        response = requests.post(
            f"{self.base_url.rstrip('/')}/tables",
            json=payload,
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def pause_consumption(self, table_name: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/tables/{table_name}/pauseConsumption",
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def resume_consumption(self, table_name: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/tables/{table_name}/resumeConsumption",
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def reload_segments(self, table_name: str) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/segments/{table_name}/reload",
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()


@dataclass
class PinotBrokerClient:
    base_url: str = "http://localhost:8099"
    timeout: int = 30

    def health(self) -> bool:
        try:
            response = requests.get(f"{self.base_url.rstrip('/')}/health", timeout=self.timeout)
            return response.ok
        except requests.RequestException:
            return False

    def query_sql(self, query: str, query_options: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"sql": query}
        if query_options:
            payload["queryOptions"] = query_options
        response = requests.post(
            f"{self.base_url.rstrip('/')}/query/sql",
            json=payload,
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def query_multistage(self, query: str, query_options: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"sql": query}
        if query_options:
            payload["queryOptions"] = query_options
        response = requests.post(
            f"{self.base_url.rstrip('/')}/query",
            json=payload,
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()

    def query_timeseries(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/query/timeseries",
            json=payload,
            timeout=self.timeout)
        _raise_for_error(response)
        return response.json()


def extract_result_rows(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    result_table = result.get("resultTable", {})
    schema = result_table.get("dataSchema", {})
    column_names = schema.get("columnNames", [])
    rows = result_table.get("rows", [])
    materialized = []
    for row in rows:
        materialized.append(dict(zip(column_names, row)))
    return materialized
