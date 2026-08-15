#!/usr/bin/env python3
from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.models import SQLRequest
from pinot_playbook_demo.service import build_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run simple latency benchmarks against demo SQL files.")
    parser.add_argument("files", nargs="+", help="Paths to .sql files")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--query-type", default="v1", choices=["v1", "multistage"])
    args = parser.parse_args()

    provider = build_provider()

    for file_name in args.files:
        sql = Path(file_name).read_text(encoding="utf-8")
        timings = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            provider.sql(SQLRequest(query=sql, query_type=args.query_type))
            timings.append((time.perf_counter() - start) * 1000)
        print(
            f"{file_name}: avg={statistics.mean(timings):.2f}ms "
            f"p95={sorted(timings)[int(0.95 * (len(timings) - 1))]:.2f}ms repeats={args.repeats}"
        )


if __name__ == "__main__":
    main()
