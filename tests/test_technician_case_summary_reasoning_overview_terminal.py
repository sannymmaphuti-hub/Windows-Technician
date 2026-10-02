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

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    case_summary = TechnicianCaseSummary(workflow)
    case_summary.set_reasoning_summary(
        reasoning_summary
    )

    return case, workflow, reasoning_summary, case_summary


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_reasoning_overview_remains_available_after_resolution():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    assert workflow.is_terminal is True
    assert case_summary.reasoning_summary is reasoning_summary
    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_reasoning_overview_remains_live_after_resolution():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    resolve_workflow(workflow)

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["findings"] == ["finding"]
    assert overview["root_causes"] == ["root-cause"]
    assert overview == reasoning_summary.overview


def test_terminal_state_does_not_modify_overview_structure():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    before = reasoning_summary.overview

    resolve_workflow(workflow)

    after = case_summary.reasoning_summary.overview

    assert set(after.keys()) == set(before.keys())
    assert after == before


def test_terminal_case_summary_and_reasoning_summary_remain_consistent():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    assert case_summary.is_terminal is True
    assert case_summary.reasoning_summary.overview == (
        reasoning_summary.overview
    )