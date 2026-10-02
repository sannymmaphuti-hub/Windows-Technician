import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def resolved_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager):
    return manager.request_reopening(
        "Technician B",
        "Issue returned after closure.",
    )


def test_recovery_record_requires_workflow():
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    with pytest.raises(ValueError):
        TechnicianReopeningRecoveryRecord(None)


def test_recovery_record_starts_empty(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    assert record.entries == []


def test_record_recovery(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    entry = record.record_recovery(reopening)

    assert entry["type"] == "REOPENING_RECOVERY"
    assert entry["status"] == "RECOVERED"
    assert entry["reopening_id"] == (
        reopening.reopening_id
    )
    assert entry["technician"] == (
        reopening.technician
    )
    assert entry["reason"] == reopening.reason


def test_record_preserves_workflow_identity(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    workflow_id = resolved_workflow.workflow_id

    manager.accept_reopening(reopening)

    entry = record.record_recovery(reopening)

    assert entry["workflow_id"] == workflow_id
    assert entry["case_id"] == resolved_workflow.case.case_id


def test_record_captures_investigating_state(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    entry = record.record_recovery(reopening)

    assert entry["workflow_state"] is (
        WorkflowState.INVESTIGATING
    )


def test_recovery_requires_accepted_reopening(
    resolved_workflow,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    with pytest.raises(ValueError):
        record.record_recovery(reopening)


def test_record_recovery_does_not_change_workflow(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    original_state = resolved_workflow.state
    original_history = resolved_workflow.history

    record.record_recovery(reopening)

    assert resolved_workflow.state == original_state
    assert resolved_workflow.history == original_history


def test_record_entries_are_read_only(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    manager.accept_reopening(reopening)
    record.record_recovery(reopening)

    entries = record.entries
    entries.clear()

    assert len(record.entries) == 1


def test_record_rejects_foreign_reopening(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_record import (
        TechnicianReopeningRecoveryRecord,
    )

    foreign_case = DiagnosticCase()
    foreign_workflow = TechnicianWorkflow(
        foreign_case
    )

    foreign_manager = (
        TechnicianCaseReopeningManager(
            foreign_workflow
        )
    )

    foreign_workflow.start_investigation()
    foreign_workflow.mark_diagnosed()
    foreign_workflow.require_action()
    foreign_workflow.start_remediation()
    foreign_workflow.start_verification()
    foreign_workflow.resolve()

    foreign_reopening = (
        foreign_manager.request_reopening(
            "Technician C",
            "Foreign issue.",
        )
    )

    record = TechnicianReopeningRecoveryRecord(
        resolved_workflow
    )

    with pytest.raises(ValueError):
        record.record_recovery(
            foreign_reopening
        )