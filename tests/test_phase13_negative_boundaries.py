from datetime import datetime, timezone

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.observability_boundary import ObservabilityBoundary
from engine.observability_event_history import ObservabilityEventHistory
from engine.operation_lifecycle_tracker import OperationLifecycleTracker
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.reliability_service import ReliabilityService
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_observability_projection import (
    TechnicianObservabilityProjection,
)
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.structured_observability_event import (
    ObservabilitySeverity,
    StructuredObservabilityEvent,
)


def make_event(event_id):
    return StructuredObservabilityEvent(
        event_id=event_id,
        event_type="boundary_test",
        severity=ObservabilitySeverity.INFO,
        occurred_at=datetime.now(timezone.utc),
        attributes={"source": "phase13_boundary_test"},
    )


def make_components():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case,
        workflow,
        WindowsDiagnosticEngineRegistry(),
    )

    reliability = ReliabilityService(workflow)

    return case, workflow, engine, reliability


def test_event_history_evicts_oldest_events_at_capacity():
    history = ObservabilityEventHistory(capacity=2)

    history.record(make_event("event-1"))
    history.record(make_event("event-2"))
    history.record(make_event("event-3"))

    snapshot = history.projection()

    assert snapshot["capacity"] == 2
    assert snapshot["event_count"] == 2
    assert snapshot["evicted_event_count"] == 1

    retained_ids = [
        event["event_id"]
        for event in snapshot["events"]
    ]

    assert retained_ids == ["event-2", "event-3"]


def test_event_history_rejects_duplicate_retained_event_ids():
    history = ObservabilityEventHistory(capacity=3)

    history.record(make_event("duplicate-event"))

    with pytest.raises(ValueError):
        history.record(make_event("duplicate-event"))

    snapshot = history.projection()

    assert snapshot["event_count"] == 1
    assert snapshot["evicted_event_count"] == 0


def test_observability_reads_do_not_mutate_diagnostic_or_reliability_state():
    _, workflow, engine, reliability = make_components()

    boundary = ObservabilityBoundary(
        engine,
        reliability,
        telemetry_enabled=False,
    )

    workflow_before = workflow.state
    engine_before = engine.projection()
    reliability_before = reliability.projection()

    for _ in range(5):
        snapshot = boundary.projection()

        assert snapshot["telemetry_enabled"] is False
        assert isinstance(snapshot["engine"], dict)
        assert isinstance(snapshot["reliability"], dict)

    assert workflow.state == workflow_before
    assert engine.projection() == engine_before
    assert reliability.projection() == reliability_before


def test_repeated_combined_projection_reads_do_not_create_operations():
    _, workflow, engine, reliability = make_components()

    boundary = ObservabilityBoundary(
        engine,
        reliability,
        telemetry_enabled=False,
    )

    history = ObservabilityEventHistory(capacity=5)

    combined = TechnicianObservabilityProjection(
        observability_boundary=boundary,
        event_history=history,
    )

    reliability_before = reliability.projection()
    history_before = history.projection()

    for _ in range(5):
        result = combined.projection()

        assert result["observability"]["telemetry_enabled"] is False
        assert result["event_history"]["event_count"] == 0

    assert reliability.projection() == reliability_before
    assert history.projection() == history_before
    assert workflow.state == engine.projection()["workflow_state"]


def test_event_history_projection_does_not_expose_mutable_internal_state():
    history = ObservabilityEventHistory(capacity=3)
    history.record(make_event("snapshot-event"))

    first = history.projection()
    first["events"].clear()

    second = history.projection()

    assert second["event_count"] == 1
    assert len(second["events"]) == 1
    assert second["events"][0]["event_id"] == "snapshot-event"
