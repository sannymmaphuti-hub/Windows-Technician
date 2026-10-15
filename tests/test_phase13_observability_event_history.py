from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

import pytest

from engine.observability_event_history import ObservabilityEventHistory
from engine.structured_observability_event import (
    ObservabilitySeverity,
    StructuredObservabilityEvent,
)


BASE_TIME = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)


def make_event(
    event_type="diagnostic.completed",
    severity=ObservabilitySeverity.INFO,
    *,
    event_id=None,
    offset=0,
    case_id="case-1",
    operation_id="operation-1",
    correlation_id="correlation-1",
    trace_id="trace-1",
    attributes=None,
):
    return StructuredObservabilityEvent(
        event_id=event_id or f"event-{offset}-{event_type}",
        event_type=event_type,
        severity=severity,
        occurred_at=BASE_TIME + timedelta(seconds=offset),
        case_id=case_id,
        operation_id=operation_id,
        correlation_id=correlation_id,
        trace_id=trace_id,
        attributes=attributes or {},
    )


def test_history_starts_empty():
    history = ObservabilityEventHistory()

    assert len(history) == 0
    assert history.projection()["event_count"] == 0
    assert history.projection()["capacity"] == 1000


def test_record_accepts_structured_event():
    history = ObservabilityEventHistory()
    event = make_event()

    result = history.record(event)

    assert result["event_id"] == event.event_id
    assert len(history) == 1


def test_record_rejects_unstructured_event():
    history = ObservabilityEventHistory()

    with pytest.raises(TypeError, match="StructuredObservabilityEvent"):
        history.record({"event_type": "diagnostic.completed"})


def test_duplicate_event_id_is_rejected():
    history = ObservabilityEventHistory()
    event = make_event(event_id="same-id")

    history.record(event)

    with pytest.raises(ValueError, match="Duplicate"):
        history.record(event)

    assert len(history) == 1


def test_query_preserves_insertion_order():
    history = ObservabilityEventHistory()
    first = make_event(event_id="first", offset=0)
    second = make_event(event_id="second", offset=1)
    third = make_event(event_id="third", offset=2)

    for event in (first, second, third):
        history.record(event)

    assert [
        item["event_id"]
        for item in history.query()
    ] == ["first", "second", "third"]


def test_query_filters_by_event_type():
    history = ObservabilityEventHistory()
    history.record(make_event("diagnostic.started", event_id="a"))
    history.record(make_event("diagnostic.completed", event_id="b"))
    history.record(make_event("operation.failed", event_id="c"))

    result = history.query(event_type="diagnostic.completed")

    assert [item["event_id"] for item in result] == ["b"]


def test_query_filters_by_severity():
    history = ObservabilityEventHistory()
    history.record(make_event(
        event_id="a",
        severity=ObservabilitySeverity.INFO,
    ))
    history.record(make_event(
        event_id="b",
        severity=ObservabilitySeverity.ERROR,
    ))

    result = history.query(severity="ERROR")

    assert [item["event_id"] for item in result] == ["b"]


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("case_id", "case-2"),
        ("operation_id", "operation-2"),
        ("correlation_id", "correlation-2"),
        ("trace_id", "trace-2"),
    ],
)
def test_query_filters_by_identifiers(field, expected):
    history = ObservabilityEventHistory()

    history.record(make_event(event_id="a"))
    history.record(make_event(
        event_id="b",
        **{field: expected},
    ))

    result = history.query(**{field: expected})

    assert [item["event_id"] for item in result] == ["b"]


def test_query_combines_multiple_filters():
    history = ObservabilityEventHistory()

    history.record(make_event(
        event_id="a",
        event_type="operation.failed",
        severity=ObservabilitySeverity.ERROR,
    ))
    history.record(make_event(
        event_id="b",
        event_type="operation.failed",
        severity=ObservabilitySeverity.WARNING,
    ))
    history.record(make_event(
        event_id="c",
        event_type="diagnostic.completed",
        severity=ObservabilitySeverity.ERROR,
    ))

    result = history.query(
        event_type="operation.failed",
        severity=ObservabilitySeverity.ERROR,
    )

    assert [item["event_id"] for item in result] == ["a"]


def test_query_filters_by_inclusive_time_range():
    history = ObservabilityEventHistory()

    for offset in range(5):
        history.record(make_event(
            event_id=f"event-{offset}",
            offset=offset,
        ))

    result = history.query(
        since=BASE_TIME + timedelta(seconds=1),
        until=BASE_TIME + timedelta(seconds=3),
    )

    assert [item["event_id"] for item in result] == [
        "event-1",
        "event-2",
        "event-3",
    ]


def test_query_limit_returns_first_matching_events():
    history = ObservabilityEventHistory()

    for offset in range(4):
        history.record(make_event(
            event_id=f"event-{offset}",
            offset=offset,
        ))

    result = history.query(limit=2)

    assert [item["event_id"] for item in result] == [
        "event-0",
        "event-1",
    ]


def test_zero_query_limit_returns_no_events():
    history = ObservabilityEventHistory()
    history.record(make_event())

    assert history.query(limit=0) == []


def test_history_evicts_oldest_event_at_capacity():
    history = ObservabilityEventHistory(capacity=2)

    history.record(make_event(event_id="a", offset=0))
    history.record(make_event(event_id="b", offset=1))
    history.record(make_event(event_id="c", offset=2))

    result = history.projection()

    assert result["event_count"] == 2
    assert result["evicted_event_count"] == 1
    assert [event["event_id"] for event in result["events"]] == [
        "b",
        "c",
    ]


def test_evicted_event_id_can_be_recorded_again():
    history = ObservabilityEventHistory(capacity=1)

    history.record(make_event(event_id="a", offset=0))
    history.record(make_event(event_id="b", offset=1))

    # Event a is no longer retained, so its ID is no longer in the
    # active duplicate-detection set.
    history.record(make_event(event_id="a", offset=2))

    assert len(history) == 1
    assert history.query()[0]["event_id"] == "a"


def test_projection_cannot_mutate_stored_history():
    history = ObservabilityEventHistory()
    history.record(make_event(
        event_id="a",
        attributes={"details": {"count": 2}},
    ))

    first = history.projection()
    first["events"][0]["event_type"] = "modified"
    first["events"][0]["attributes"]["details"]["count"] = 999
    first["events"].clear()

    second = history.projection()

    assert second["event_count"] == 1
    assert second["events"][0]["event_type"] == "diagnostic.completed"
    assert second["events"][0]["attributes"]["details"]["count"] == 2


def test_query_results_cannot_mutate_stored_history():
    history = ObservabilityEventHistory()
    history.record(make_event(
        event_id="a",
        attributes={"items": ["original"]},
    ))

    result = history.query()
    result[0]["attributes"]["items"].append("modified")
    result[0]["event_type"] = "modified"

    second = history.query()

    assert second[0]["attributes"]["items"] == ["original"]
    assert second[0]["event_type"] == "diagnostic.completed"


@pytest.mark.parametrize("capacity", [0, -1])
def test_capacity_must_be_positive(capacity):
    with pytest.raises(ValueError, match="at least 1"):
        ObservabilityEventHistory(capacity=capacity)


@pytest.mark.parametrize("capacity", [True, 1.5, "5"])
def test_capacity_must_be_integer(capacity):
    with pytest.raises(TypeError, match="integer"):
        ObservabilityEventHistory(capacity=capacity)


@pytest.mark.parametrize("limit", [-1, True, 1.5, "2"])
def test_query_rejects_invalid_limits(limit):
    history = ObservabilityEventHistory()

    with pytest.raises((TypeError, ValueError)):
        history.query(limit=limit)


def test_query_rejects_invalid_time_range():
    history = ObservabilityEventHistory()

    with pytest.raises(ValueError, match="since cannot be later"):
        history.query(
            since=BASE_TIME + timedelta(seconds=2),
            until=BASE_TIME,
        )


def test_query_rejects_naive_datetime():
    history = ObservabilityEventHistory()

    with pytest.raises(ValueError, match="timezone-aware"):
        history.query(since=datetime(2026, 10, 8, 12, 0))


def test_query_rejects_blank_identifier_filter():
    history = ObservabilityEventHistory()

    with pytest.raises(ValueError, match="case_id"):
        history.query(case_id="  ")


def test_history_is_safe_for_concurrent_recording():
    history = ObservabilityEventHistory(capacity=500)

    def record_one(index):
        history.record(make_event(
            event_id=f"concurrent-{index}",
            offset=index,
        ))

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(record_one, range(200)))

    assert len(history) == 200
    assert len(history.query()) == 200
    assert history.projection()["evicted_event_count"] == 0


def test_history_is_safe_for_concurrent_queries_and_recording():
    history = ObservabilityEventHistory(capacity=500)

    def record_one(index):
        history.record(make_event(
            event_id=f"mixed-{index}",
            offset=index,
        ))

    def query_history(_):
        return history.query(limit=20)

    with ThreadPoolExecutor(max_workers=8) as executor:
        record_futures = [
            executor.submit(record_one, index)
            for index in range(100)
        ]
        query_futures = [
            executor.submit(query_history, index)
            for index in range(100)
        ]

        for future in record_futures + query_futures:
            future.result()

    assert len(history) == 100
    assert len(history.query()) == 100
