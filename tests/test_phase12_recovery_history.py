import pytest

from engine.recovery_execution_boundary import (
    RecoveryApprovalDecision,
    RecoveryApprovalStatus,
)
from engine.recovery_history import RecoveryHistory


def make_decision(
    plan_id="plan-1",
    operation_id="operation-1",
    status=RecoveryApprovalStatus.DENIED,
):
    return RecoveryApprovalDecision(
        plan_id=plan_id,
        operation_id=operation_id,
        status=status,
        reason="Recovery approval reviewed",
    )


def test_history_records_decision():
    history = RecoveryHistory()
    entry = history.record(make_decision())

    assert entry.plan_id == "plan-1"
    assert entry.status == "DENIED"


def test_history_rejects_duplicate_plan_operation_pair():
    history = RecoveryHistory()
    history.record(make_decision())

    with pytest.raises(ValueError):
        history.record(make_decision())


def test_history_accepts_distinct_operations():
    history = RecoveryHistory()
    history.record(make_decision(operation_id="operation-1"))
    history.record(make_decision(operation_id="operation-2"))

    assert len(history.entries) == 2


def test_history_accepts_distinct_plans_for_same_operation():
    history = RecoveryHistory()
    history.record(make_decision(plan_id="plan-1"))
    history.record(make_decision(plan_id="plan-2"))

    assert len(history.entries) == 2


def test_entries_are_returned_as_tuple():
    history = RecoveryHistory()
    history.record(make_decision())

    assert isinstance(history.entries, tuple)


def test_projection_counts_decisions_by_status():
    history = RecoveryHistory()
    history.record(make_decision(status=RecoveryApprovalStatus.DENIED))
    history.record(
        make_decision(
            plan_id="plan-2",
            status=RecoveryApprovalStatus.APPROVED,
        )
    )

    projection = history.projection()

    assert projection["total"] == 2
    assert projection["by_status"]["DENIED"] == 1
    assert projection["by_status"]["APPROVED"] == 1


def test_invalid_decision_is_rejected():
    with pytest.raises(TypeError):
        RecoveryHistory().record(object())


def test_recorded_entries_are_immutable():
    history = RecoveryHistory()
    entry = history.record(make_decision())

    with pytest.raises((AttributeError, TypeError)):
        entry.status = "APPROVED"


def test_projection_contains_recorded_reason():
    history = RecoveryHistory()
    history.record(make_decision())

    assert (
        history.projection()["entries"][0]["reason"]
        == "Recovery approval reviewed"
    )
