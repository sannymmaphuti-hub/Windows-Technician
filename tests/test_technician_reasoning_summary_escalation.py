from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_workflow import WorkflowState


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

    return summary, workflow


def test_summary_tracks_escalated_workflow():
    summary, workflow = create_summary()

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert summary.workflow is workflow


def test_summary_workflow_id_remains_stable_after_escalation():
    summary, workflow = create_summary()

    original_workflow_id = summary.workflow_id

    workflow.escalate()

    assert summary.workflow_id == original_workflow_id


def test_summary_case_id_remains_stable_after_escalation():
    summary, workflow = create_summary()

    original_case_id = summary.case_id

    workflow.escalate()

    assert summary.case_id == original_case_id


def test_summary_remains_terminal_after_escalation():
    summary, workflow = create_summary()

    workflow.escalate()

    assert workflow.is_terminal is True
    assert summary.workflow.is_terminal is True