import pytest

from engine.operation_lifecycle_tracker import (
    OperationLifecycleTracker,
    OperationStatus,
)


def test_create_operation_starts_pending():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")

    assert record.status is OperationStatus.PENDING
    assert record.operation_type == "diagnostic"
    assert record.operation_id


def test_operation_can_complete_successfully():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")

    tracker.transition(record.operation_id, OperationStatus.RUNNING)
    completed = tracker.transition(
        record.operation_id, OperationStatus.SUCCEEDED
    )

    assert completed.status is OperationStatus.SUCCEEDED


def test_operation_failure_requires_reason():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")
    tracker.transition(record.operation_id, OperationStatus.RUNNING)

    with pytest.raises(ValueError):
        tracker.transition(record.operation_id, OperationStatus.FAILED)


def test_failed_operation_records_reason():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")
    tracker.transition(record.operation_id, OperationStatus.RUNNING)

    failed = tracker.transition(
        record.operation_id,
        OperationStatus.FAILED,
        failure_reason="Diagnostic provider unavailable",
    )

    assert failed.failure_reason == "Diagnostic provider unavailable"


def test_terminal_operation_cannot_restart():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")
    tracker.transition(record.operation_id, OperationStatus.CANCELLED)

    with pytest.raises(ValueError):
        tracker.transition(record.operation_id, OperationStatus.RUNNING)


def test_unknown_operation_is_rejected():
    tracker = OperationLifecycleTracker()

    with pytest.raises(KeyError):
        tracker.get("unknown-operation")


def test_projection_reports_operation_counts():
    tracker = OperationLifecycleTracker()
    tracker.create("diagnostic")
    tracker.create("health_check")

    projection = tracker.projection()

    assert projection["total"] == 2
    assert projection["by_status"]["PENDING"] == 2


def test_records_are_exposed_as_immutable_snapshot():
    tracker = OperationLifecycleTracker()
    tracker.create("diagnostic")

    assert isinstance(tracker.records, tuple)


def test_invalid_operation_type_is_rejected():
    tracker = OperationLifecycleTracker()

    with pytest.raises(ValueError):
        tracker.create("")


def test_transition_requires_enum_status():
    tracker = OperationLifecycleTracker()
    record = tracker.create("diagnostic")

    with pytest.raises(ValueError):
        tracker.transition(record.operation_id, "RUNNING")
