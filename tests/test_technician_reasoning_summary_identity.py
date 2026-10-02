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

    return summary, case, workflow


def test_exposes_case_id():
    summary, case, _ = create_summary()

    assert summary.case_id == case.case_id


def test_exposes_workflow_id():
    summary, _, workflow = create_summary()

    assert summary.workflow_id == workflow.workflow_id


def test_case_id_matches_workflow_case():
    summary, _, workflow = create_summary()

    assert summary.case_id == workflow.case.case_id


def test_workflow_id_matches_workflow():
    summary, _, workflow = create_summary()

    assert summary.workflow_id == workflow.workflow_id


def test_identity_does_not_create_new_case_id():
    summary, case, _ = create_summary()

    assert summary.case_id is case.case_id


def test_identity_does_not_create_new_workflow_id():
    summary, _, workflow = create_summary()

    assert summary.workflow_id is workflow.workflow_id