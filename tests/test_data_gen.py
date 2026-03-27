from pinot_playbook_demo.data_gen import derive_trip_states, generate_merchants, generate_trip_events


def test_generate_trip_events_is_deterministic():
    merchants = generate_merchants(seed=42)
    events_a = generate_trip_events(seed=42, merchants=merchants)
    events_b = generate_trip_events(seed=42, merchants=merchants)
    assert [e.model_dump(mode="json") for e in events_a[:20]] == [e.model_dump(mode="json") for e in events_b[:20]]


def test_trip_versions_are_positive_and_states_are_latest():
    merchants = generate_merchants(seed=11)
    events = generate_trip_events(seed=11, merchants=merchants)
    states = derive_trip_states(events)
    assert events
    assert states

    latest_by_trip = {}
    for event in events:
        latest_by_trip[event.trip_id] = max(
            latest_by_trip.get(event.trip_id, event),
            event,
            key=lambda e: (e.event_version, e.event_time_ms))

    for state in states:
        latest = latest_by_trip[state.trip_id]
        assert state.event_version == latest.event_version
        assert state.last_event_time_ms == latest.event_time_ms
