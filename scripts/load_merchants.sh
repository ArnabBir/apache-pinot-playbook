#!/usr/bin/env bash
set -euo pipefail

python3 scripts/generate_merchants.py --output data/merchants.csv
docker compose exec -T pinot-controller bash -lc "bin/pinot-admin.sh LaunchDataIngestionJob -jobSpecFile /workspace/jobs/merchants.job.yml"

echo "Launched offline ingestion job for merchants_dim."
