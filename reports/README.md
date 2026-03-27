# Simulation Summary

This directory contains generated outputs from the deterministic simulation utilities.

## Segment pruning

- total segments observed: `506`
- scanned rows without pruning: `1611`
- scanned rows with time pruning: `23`
- scanned rows with time + city pruning: `13`
- total pruning gain: `99.19%`

## Star-tree intuition

- raw rows: `1611`
- aggregate cells: `18`
- compression ratio: `89.5`

Top groups:

- `pune / economy` -> count=214, gmv=11141.12
- `hyderabad / economy` -> count=191, gmv=10244.82
- `chennai / economy` -> count=214, gmv=10049.34
- `delhi / economy` -> count=206, gmv=9434.26
- `bengaluru / economy` -> count=213, gmv=8064.12

## Upsert intuition

- input events: `1611`
- distinct trip ids: `400`
- latest-state rows: `400`
- active states: `383`
- deleted states: `17`

Use these reports together with:

- [`scripts/simulate_segment_pruning.py`](scripts/simulate_segment_pruning.py)
- [`scripts/simulate_star_tree.py`](scripts/simulate_star_tree.py)
- [`scripts/simulate_upsert.py`](scripts/simulate_upsert.py)
