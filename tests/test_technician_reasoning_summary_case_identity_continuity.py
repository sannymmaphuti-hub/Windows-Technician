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

    return summary, case, workflow, history


def test_case_identity_is_preserved_during_investigation():
    summary, case, workflow, _ = create_summary()

    workflow.start_investigation()

    assert summary.case_id == case.case_id


def test_case_identity_is_preserved_during_recovery():
    summary, case, workflow, history = create_summary()

    workflow.start_investigation()

    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    assert summary.case_id == case.case_id


def test_case_identity_is_preserved_during_remediation():
    summary, case, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.case_id == case.case_id


def test_case_identity_is_preserved_during_verification():
    summary, case, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert summary.case_id == case.case_id


def test_case_identity_is_preserved_after_resolution():
    summary, case, workflow, _ = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.case_id == case.case_id


def test_case_identity_is_preserved_after_escalation():
    summary, case, workflow, _ = create_summary()

    workflow.escalate()

    assert summary.case_id == case.case_id