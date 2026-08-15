#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.data_gen import (
    derive_trip_states,
    events_to_rows,
    generate_merchants,
    generate_trip_events,
    states_to_rows,
    write_jsonl,
    write_kafka_lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic trip events and state updates.")
    parser.add_argument("--trips", type=int, default=400)
    parser.add_argument("--max-updates", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--events-output", default="data/sample_trip_events.jsonl")
    parser.add_argument("--state-output", default="data/sample_trip_state.jsonl")
    parser.add_argument("--kafka-output", default="data/sample_trip_events.kafka.txt")
    parser.add_argument("--state-kafka-output", default="data/sample_trip_state.kafka.txt")
    args = parser.parse_args()

    merchants = generate_merchants(seed=args.seed)
    events = generate_trip_events(
        n_trips=args.trips,
        max_updates=args.max_updates,
        seed=args.seed,
        merchants=merchants)
    states = derive_trip_states(events)

    event_rows = events_to_rows(events)
    state_rows = states_to_rows(states)

    events_file = write_jsonl(event_rows, args.events_output)
    states_file = write_jsonl(state_rows, args.state_output)
    kafka_events = write_kafka_lines(event_rows, "trip_id", args.kafka_output)
    kafka_states = write_kafka_lines(state_rows, "trip_id", args.state_kafka_output)

    print(f"Wrote {len(event_rows)} trip events to {Path(events_file).resolve()}")
    print(f"Wrote {len(state_rows)} trip state rows to {Path(states_file).resolve()}")
    print(f"Wrote keyed Kafka payloads to {Path(kafka_events).resolve()} and {Path(kafka_states).resolve()}")


if __name__ == "__main__":
    main()
