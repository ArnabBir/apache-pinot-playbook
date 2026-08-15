#!/usr/bin/env bash
set -euo pipefail

python3 scripts/generate_contracts.py
python3 scripts/generate_merchants.py --output data/merchants.csv
python3 scripts/produce_trip_events.py --events-output data/sample_trip_events.jsonl --state-output data/sample_trip_state.jsonl --kafka-output data/sample_trip_events.kafka.txt --state-kafka-output data/sample_trip_state.kafka.txt

docker compose up -d
bash scripts/create_topics.sh
python3 scripts/setup_pinot.py --wait
bash scripts/load_merchants.sh
bash scripts/stream_trip_events.sh

echo "Bootstrap complete. Pinot controller: http://localhost:9000, broker: http://localhost:8099, demo API: http://localhost:8010"
