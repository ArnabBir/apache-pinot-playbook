#!/usr/bin/env bash
set -euo pipefail

python scripts/produce_trip_events.py

docker compose exec -T kafka kafka-console-producer --bootstrap-server localhost:19092 --topic trip-events --property parse.key=true --property key.separator='|' < data/sample_trip_events.kafka.txt
docker compose exec -T kafka kafka-console-producer --bootstrap-server localhost:19092 --topic trip-state --property parse.key=true --property key.separator='|' < data/sample_trip_state.kafka.txt

echo "Streamed trip-events and trip-state records into Kafka."
