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


def test_overview_remains_available_during_workflow_lifecycle():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    assert case_summary.reasoning_summary.overview == (
        reasoning_summary.overview
    )

    workflow.mark_diagnosed()

    assert case_summary.reasoning_summary.overview == (
        reasoning_summary.overview
    )


def test_overview_remains_available_after_resolution():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.is_terminal is True
    assert case_summary.reasoning_summary.overview == (
        reasoning_summary.overview
    )


def test_overview_tracks_case_evidence_across_lifecycle():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    case.findings.append("finding")

    assert case_summary.reasoning_summary.overview[
        "finding_count"
    ] == 1

    workflow.mark_diagnosed()

    case.root_causes.append("root-cause")

    assert case_summary.reasoning_summary.overview[
        "root_cause_count"
    ] == 1

    workflow.require_action()

    case.recommendations.append("recommendation")

    assert case_summary.reasoning_summary.overview[
        "recommendation_count"
    ] == 1

    assert case_summary.reasoning_summary.overview == (
        reasoning_summary.overview
    )


def test_overview_does_not_depend_on_workflow_state_snapshot():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    first = case_summary.reasoning_summary.overview

    workflow.start_investigation()

    second = case_summary.reasoning_summary.overview

    assert first == second
    assert second == reasoning_summary.overview