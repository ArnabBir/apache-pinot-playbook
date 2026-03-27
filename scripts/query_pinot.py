#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.models import SQLRequest
from pinot_playbook_demo.service import build_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a SQL query through the demo provider or Pinot.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sql")
    group.add_argument("--file")
    parser.add_argument("--query-type", default="v1", choices=["v1", "multistage"])
    parser.add_argument("--query-options", default=None)
    args = parser.parse_args()

    sql = args.sql or Path(args.file).read_text(encoding="utf-8")
    provider = build_provider()
    result = provider.sql(SQLRequest(query=sql, query_type=args.query_type, query_options=args.query_options))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
