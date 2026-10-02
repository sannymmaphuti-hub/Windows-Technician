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


def test_case_id_is_read_only():
    summary, _, _ = create_summary()

    try:
        summary.case_id = "different-case"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "case_id must be read-only."
        )


def test_workflow_id_is_read_only():
    summary, _, _ = create_summary()

    try:
        summary.workflow_id = "different-workflow"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "workflow_id must be read-only."
        )


def test_case_id_remains_unchanged():
    summary, case, _ = create_summary()

    original_case_id = case.case_id

    assert summary.case_id == original_case_id


def test_workflow_id_remains_unchanged():
    summary, _, workflow = create_summary()

    original_workflow_id = workflow.workflow_id

    assert summary.workflow_id == original_workflow_id