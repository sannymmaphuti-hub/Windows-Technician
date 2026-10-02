import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_recovery_cycle_audit import (
    TechnicianRecoveryCycleAudit,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(
        DiagnosticCase()
    )
    workflow.start_investigation()
    return workflow


@pytest.fixture
def history(workflow):
    return TechnicianRecoveryCycleHistory(
        workflow
    )


def test_audit_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianRecoveryCycleAudit(None)


def test_audit_starts_empty(workflow):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    assert audit.entries == []


def test_record_cycle(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    entry = audit.record_cycle(cycle)

    assert entry["type"] == "RECOVERY_CYCLE"
    assert entry["cycle_number"] == 1
    assert entry["workflow_id"] == workflow.workflow_id


def test_record_cycle_contains_timestamp(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    entry = audit.record_cycle(cycle)

    assert entry["started_at"] == cycle.started_at


def test_record_cycle_contains_kind(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    entry = audit.record_cycle(cycle)

    assert entry["is_recovery"] is True
    assert entry["is_original"] is False


def test_original_cycle_is_recorded(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=0,
    )

    entry = audit.record_cycle(cycle)

    assert entry["cycle_number"] == 0
    assert entry["is_original"] is True


def test_different_workflow_is_rejected(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    other_workflow = TechnicianWorkflow(
        DiagnosticCase()
    )

    cycle = TechnicianRecoveryCycle(
        other_workflow,
        cycle_number=1,
    )

    with pytest.raises(ValueError):
        audit.record_cycle(cycle)


def test_entries_are_read_only(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    audit.record_cycle(cycle)

    entries = audit.entries
    entries.clear()

    assert len(audit.entries) == 1


def test_audit_does_not_change_workflow(
    workflow,
):
    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    original_history = workflow.history

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    audit.record_cycle(cycle)

    assert workflow.history == original_history