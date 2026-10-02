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
from engine.technician_recovery_cycle_report import (
    TechnicianRecoveryCycleReport,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


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


@pytest.fixture
def audit(workflow):
    return TechnicianRecoveryCycleAudit(
        workflow
    )


def test_report_requires_history():
    with pytest.raises(ValueError):
        TechnicianRecoveryCycleReport(None)


def test_report_starts_with_original_cycle(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.cycle_count == 1
    assert report.current_cycle_number == 0
    assert report.is_recovery is False


def test_report_exposes_current_cycle(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.current_cycle is history.latest_cycle


def test_report_exposes_started_at(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    assert (
        report.started_at
        == history.latest_cycle.started_at
    )


def test_report_exposes_outcome(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.outcome == "ACTIVE"


def test_report_updates_after_recovery_cycle(
    workflow,
    history,
):
    recovery_cycle = history.latest_cycle.start_recovery_cycle()

    history.record_cycle(
        recovery_cycle
    )

    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.cycle_count == 2
    assert report.current_cycle_number == 1
    assert report.is_recovery is True
    assert report.current_cycle is recovery_cycle


def test_report_reflects_resolved_outcome(
    workflow,
    history,
):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    
    workflow.resolve()

    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.outcome == "RESOLVED"


def test_report_reflects_escalated_outcome(
    workflow,
    history,
):
    workflow.escalate()

    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.outcome == "ESCALATED"


def test_report_is_read_only(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    cycles = report.cycles
    cycles.clear()

    assert report.cycle_count == 1


def test_report_does_not_change_workflow(
    workflow,
    history,
):
    original_state = workflow.state
    original_history = workflow.history

    TechnicianRecoveryCycleReport(
        history
    )

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_report_exposes_audit_entries(
    workflow,
):
    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    audit = TechnicianRecoveryCycleAudit(
        workflow
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)
    audit.record_cycle(cycle)

    report = TechnicianRecoveryCycleReport(
        history,
        audit=audit,
    )

    assert len(report.audit_entries) == 1
    assert (
        report.audit_entries[0]["cycle_number"]
        == 1
    )


def test_report_without_audit_has_empty_audit_entries(
    history,
):
    report = TechnicianRecoveryCycleReport(
        history
    )

    assert report.audit_entries == []