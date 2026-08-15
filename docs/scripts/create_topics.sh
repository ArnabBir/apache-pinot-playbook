#!/usr/bin/env bash
set -euo pipefail

docker compose exec -T kafka kafka-topics --bootstrap-server localhost:19092 --create --if-not-exists --topic trip-events --partitions 4 --replication-factor 1
docker compose exec -T kafka kafka-topics --bootstrap-server localhost:19092 --create --if-not-exists --topic trip-state --partitions 4 --replication-factor 1

echo "Kafka topics trip-events and trip-state are ready."
