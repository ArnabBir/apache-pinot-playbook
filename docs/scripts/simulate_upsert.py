#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root / "src"))
sys.path.insert(0, str(_repo_root))

from pinot_playbook_demo.data_gen import generate_trip_events
from pinot_playbook_demo.simulations import simulate_upsert


def main() -> None:
    events = generate_trip_events()
    report = simulate_upsert(events)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
