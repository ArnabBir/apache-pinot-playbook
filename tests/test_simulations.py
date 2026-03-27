from pinot_playbook_demo.data_gen import generate_merchants, generate_trip_events
from pinot_playbook_demo.simulations import (
    simulate_partition_skew,
    simulate_segment_pruning,
    simulate_star_tree,
    simulate_upsert)


def _events():
    merchants = generate_merchants(seed=42)
    return generate_trip_events(seed=42, merchants=merchants)


def test_segment_pruning_reduces_scanned_rows():
    events = _events()
    start_ms = min(e.event_time_ms for e in events)
    report = simulate_segment_pruning(events, city_filter="bengaluru", start_ms=start_ms, end_ms=start_ms + 2 * 3600 * 1000)
    assert report["scanned_rows_with_time_pruning"] <= report["scanned_rows_without_pruning"]
    assert report["scanned_rows_with_time_and_city_pruning"] <= report["scanned_rows_with_time_pruning"]


def test_star_tree_compresses_group_space():
    events = _events()
    report = simulate_star_tree(events)
    assert report["aggregate_cells"] < report["raw_rows"]
    assert report["compression_ratio"] > 1


def test_upsert_collapses_to_latest_state():
    events = _events()
    report = simulate_upsert(events)
    assert report["latest_state_rows"] <= report["input_event_rows"]
    assert report["distinct_trip_ids"] == report["latest_state_rows"]


def test_partition_skew_is_reasonable_for_deterministic_generator():
    events = _events()
    report = simulate_partition_skew(events)
    assert report["skew_ratio"] < 2.5
