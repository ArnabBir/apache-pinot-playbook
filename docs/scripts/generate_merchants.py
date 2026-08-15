#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.data_gen import generate_merchants, merchants_to_rows, write_csv_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate merchant dimension CSV for the Pinot demo.")
    parser.add_argument("--count", type=int, default=36)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/merchants.csv")
    args = parser.parse_args()

    merchants = generate_merchants(n=args.count, seed=args.seed)
    rows = merchants_to_rows(merchants)
    fieldnames = list(rows[0].keys()) if rows else []
    path = write_csv_rows(rows, args.output, fieldnames)
    print(f"Wrote {len(rows)} merchants to {Path(path).resolve()}")


if __name__ == "__main__":
    main()
