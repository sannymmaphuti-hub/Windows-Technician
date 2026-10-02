from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_context():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(
        workflow
    )

    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    )


def test_reasoning_summary_tracks_workflow_state():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        _,
    ) = create_context()

    assert reasoning_summary.workflow.state is workflow.state

    workflow.start_investigation()

    assert reasoning_summary.workflow.state is workflow.state


def test_reasoning_summary_tracks_same_case():
    (
        case,
        workflow,
        _,
        reasoning_summary,
        _,
    ) = create_context()

    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.workflow.case is case


def test_case_summary_retains_reasoning_summary_after_workflow_transition():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        case_summary,
    ) = create_context()

    workflow.start_investigation()

    assert case_summary.reasoning_summary is reasoning_summary
    assert (
        case_summary.reasoning_summary.workflow
        is workflow
    )


def test_reasoning_summary_does_not_own_workflow_state():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        _,
    ) = create_context()

    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.workflow.state.value == "OPEN"

    workflow.start_investigation()

    assert reasoning_summary.workflow.state.value == "INVESTIGATING"


def test_reasoning_summary_does_not_create_separate_case():
    (
        case,
        _,
        _,
        reasoning_summary,
        _,
    ) = create_context()

    assert reasoning_summary.workflow.case is case