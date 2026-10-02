from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summaries():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(workflow)
    case_summary.set_reasoning_summary(reasoning_summary)

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    )


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_terminal_overview_does_not_expose_workflow_reference():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert workflow not in overview.values()
    assert "workflow" not in overview


def test_terminal_overview_does_not_expose_recovery_history_reference():
    (
        _,
        workflow,
        history,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert history not in overview.values()
    assert "cycle_history" not in overview


def test_mutating_terminal_overview_does_not_mutate_workflow():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview
    overview["workflow"] = workflow
    overview["workflow_state"] = workflow.state

    fresh_overview = (
        case_summary.reasoning_summary.overview
    )

    assert "workflow" not in fresh_overview
    assert "workflow_state" not in fresh_overview


def test_terminal_overview_remains_isolated_from_case_and_history():
    (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    overview["case"] = case
    overview["cycle_history"] = history
    overview["summary"] = reasoning_summary

    fresh_overview = (
        case_summary.reasoning_summary.overview
    )

    assert "case" not in fresh_overview
    assert "cycle_history" not in fresh_overview
    assert "summary" not in fresh_overview

    assert (
        case_summary.reasoning_summary
        is reasoning_summary
    )