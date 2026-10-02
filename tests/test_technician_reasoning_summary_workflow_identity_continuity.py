from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary, workflow, history


def test_workflow_identity_is_preserved_during_investigation():
    summary, workflow, _ = create_summary()

    workflow.start_investigation()

    assert summary.workflow_id == workflow.workflow_id


def test_workflow_identity_is_preserved_during_recovery():
    summary, workflow, history = create_summary()

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    assert summary.workflow_id == workflow.workflow_id


def test_workflow_identity_is_preserved_during_remediation():
    summary, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.workflow_id == workflow.workflow_id


def test_workflow_identity_is_preserved_during_verification():
    summary, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert summary.workflow_id == workflow.workflow_id


def test_workflow_identity_is_preserved_after_resolution():
    summary, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.workflow_id == workflow.workflow_id


def test_workflow_identity_is_preserved_after_escalation():
    summary, workflow, _ = create_summary()

    workflow.escalate()

    assert summary.workflow_id == workflow.workflow_id