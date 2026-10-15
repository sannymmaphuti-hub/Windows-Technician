from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from engine.structured_observability_event import (
    ObservabilitySeverity,
    StructuredObservabilityEvent,
)


def test_event_generates_unique_ids():
    first = StructuredObservabilityEvent(event_type="diagnostic.started")
    second = StructuredObservabilityEvent(event_type="diagnostic.started")

    assert first.event_id
    assert first.event_id != second.event_id


def test_event_defaults_to_info_severity():
    event = StructuredObservabilityEvent(event_type="diagnostic.started")

    assert event.severity is ObservabilitySeverity.INFO


@pytest.mark.parametrize(
    "severity",
    ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
)
def test_event_accepts_valid_severity_strings(severity):
    event = StructuredObservabilityEvent(
        event_type="operation.failed",
        severity=severity,
    )

    assert event.severity.value == severity


def test_event_rejects_invalid_severity():
    with pytest.raises(ValueError, match="severity"):
        StructuredObservabilityEvent(
            event_type="operation.failed",
            severity="UNKNOWN",
        )


@pytest.mark.parametrize("event_type", ["", "   ", None])
def test_event_rejects_invalid_event_type(event_type):
    with pytest.raises(ValueError, match="event_type"):
        StructuredObservabilityEvent(event_type=event_type)


def test_event_normalizes_timestamp_to_utc():
    timestamp = datetime(
        2026, 10, 8, 12, 0,
        tzinfo=timezone(timedelta(hours=2)),
    )
    event = StructuredObservabilityEvent(
        event_type="operation.completed",
        occurred_at=timestamp,
    )

    assert event.occurred_at.tzinfo is timezone.utc
    assert event.occurred_at.hour == 10
    assert event.projection()["occurred_at"].endswith("+00:00")


def test_event_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        StructuredObservabilityEvent(
            event_type="operation.completed",
            occurred_at=datetime(2026, 10, 8, 12, 0),
        )


def test_event_preserves_correlation_identifiers():
    event = StructuredObservabilityEvent(
        event_type="diagnostic.completed",
        case_id="case-1",
        operation_id="operation-1",
        correlation_id="correlation-1",
        trace_id="trace-1",
    )

    result = event.projection()
    assert result["case_id"] == "case-1"
    assert result["operation_id"] == "operation-1"
    assert result["correlation_id"] == "correlation-1"
    assert result["trace_id"] == "trace-1"


def test_event_is_immutable():
    event = StructuredObservabilityEvent(event_type="diagnostic.started")

    with pytest.raises(FrozenInstanceError):
        event.event_type = "operation.failed"


def test_attributes_are_detached_from_input():
    source = {"component": "diagnostics", "details": {"count": 2}}
    event = StructuredObservabilityEvent(
        event_type="diagnostic.completed",
        attributes=source,
    )

    source["component"] = "modified"
    source["details"]["count"] = 99

    projected = event.projection()
    assert projected["attributes"]["component"] == "diagnostics"
    assert projected["attributes"]["details"]["count"] == 2


def test_event_attributes_are_immutable():
    event = StructuredObservabilityEvent(
        event_type="diagnostic.completed",
        attributes={"component": "diagnostics"},
    )

    with pytest.raises(TypeError):
        event.attributes["component"] = "modified"


def test_projection_is_detached_from_event():
    event = StructuredObservabilityEvent(
        event_type="diagnostic.completed",
        attributes={"details": {"count": 2}, "labels": ["a", "b"]},
    )

    first = event.projection()
    first["attributes"]["details"]["count"] = 99
    first["attributes"]["labels"].append("c")

    second = event.projection()
    assert second["attributes"]["details"]["count"] == 2
    assert second["attributes"]["labels"] == ["a", "b"]


@pytest.mark.parametrize(
    "field_name",
    ["case_id", "operation_id", "correlation_id", "trace_id"],
)
def test_optional_identifiers_reject_blank_strings(field_name):
    with pytest.raises(ValueError, match=field_name):
        StructuredObservabilityEvent(
            event_type="diagnostic.completed",
            **{field_name: "   "},
        )


def test_event_rejects_non_mapping_attributes():
    with pytest.raises(TypeError, match="attributes"):
        StructuredObservabilityEvent(
            event_type="diagnostic.completed",
            attributes=["not", "a", "mapping"],
        )


def test_event_rejects_unsupported_attribute_objects():
    with pytest.raises(TypeError, match="Event attributes"):
        StructuredObservabilityEvent(
            event_type="diagnostic.completed",
            attributes={"unexpected": object()},
        )


def test_event_rejects_blank_attribute_keys():
    with pytest.raises(ValueError, match="Attribute keys"):
        StructuredObservabilityEvent(
            event_type="diagnostic.completed",
            attributes={" ": "invalid"},
        )


def test_projection_contains_complete_schema():
    event = StructuredObservabilityEvent(
        event_type="operation.failed",
        severity=ObservabilitySeverity.ERROR,
        case_id="case-1",
        operation_id="operation-1",
        correlation_id="correlation-1",
        trace_id="trace-1",
        attributes={"reason_code": "timeout"},
    )

    assert set(event.projection()) == {
        "event_id",
        "event_type",
        "severity",
        "occurred_at",
        "case_id",
        "operation_id",
        "correlation_id",
        "trace_id",
        "attributes",
    }
