#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.pinot_client import PinotControllerClient, PinotError


def create_kafka_topics(table_dir: Path, kafka_container: str = "pinot-kafka",
                        bootstrap_server: str = "localhost:9092",
                        partitions: int = 4, replication_factor: int = 1) -> None:
    """Extract topic names from real-time table configs and create them in Kafka."""
    for table_path in sorted(table_dir.glob("*.json")):
        try:
            config = json.loads(table_path.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        if config.get("tableType") != "REALTIME":
            continue

        stream_configs = (config.get("ingestionConfig", {})
                          .get("streamIngestionConfig", {})
                          .get("streamConfigMaps", []))
        for sc in stream_configs:
            topic = sc.get("stream.kafka.topic.name")
            if not topic:
                continue
            try:
                subprocess.run(
                    ["docker", "exec", kafka_container,
                     "kafka-topics", "--create", "--topic", topic,
                     "--bootstrap-server", bootstrap_server,
                     "--partitions", str(partitions),
                     "--replication-factor", str(replication_factor)],
                    check=True, capture_output=True, text=True,
                )
                print(f"Created Kafka topic: {topic}")
            except subprocess.CalledProcessError as exc:
                if "already exists" in exc.stderr.lower():
                    print(f"Kafka topic {topic} already exists; continuing")
                else:
                    raise RuntimeError(f"Failed to create topic {topic}: {exc.stderr}") from exc


def upload_all(controller: PinotControllerClient, schema_dir: Path, table_dir: Path) -> None:
    for schema_path in sorted(schema_dir.glob("*.json")):
        try:
            response = controller.create_schema(schema_path)
            print(f"Uploaded schema {schema_path.name}: {response}")
        except PinotError as exc:
            if "already exists" in str(exc).lower():
                print(f"Schema {schema_path.name} already exists; continuing")
            else:
                raise

    for table_path in sorted(table_dir.glob("*.json")):
        try:
            response = controller.create_table(table_path)
            print(f"Uploaded table {table_path.name}: {response}")
        except PinotError as exc:
            if "already exists" in str(exc).lower():
                print(f"Table {table_path.name} already exists; continuing")
            else:
                raise


def wait_for_controller(controller: PinotControllerClient, timeout_seconds: int = 120) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if controller.health():
            return
        print("Waiting for Pinot controller...")
        time.sleep(2)
    raise RuntimeError(f"Pinot controller at {controller.base_url} did not become ready in time.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload the demo schemas and tables to Pinot.")
    parser.add_argument("--controller-url", default="http://localhost:9000")
    parser.add_argument("--schema-dir", default="schemas")
    parser.add_argument("--table-dir", default="tables")
    parser.add_argument("--kafka-container", default="pinot-kafka")
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()

    create_kafka_topics(Path(args.table_dir), kafka_container=args.kafka_container)

    controller = PinotControllerClient(base_url=args.controller_url)
    if args.wait:
        wait_for_controller(controller)
    upload_all(controller, Path(args.schema_dir), Path(args.table_dir))


if __name__ == "__main__":
    main()
