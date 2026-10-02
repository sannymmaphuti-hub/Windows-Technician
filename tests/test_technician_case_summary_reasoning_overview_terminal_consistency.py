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


def test_terminal_overview_counts_match_collections():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.extend(["finding-1", "finding-2"])
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.extend(
        ["recommendation-1", "recommendation-2"]
    )

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == len(
        overview["findings"]
    )
    assert overview["correlation_count"] == len(
        overview["correlations"]
    )
    assert overview["root_cause_count"] == len(
        overview["root_causes"]
    )
    assert overview["recommendation_count"] == len(
        overview["recommendations"]
    )


def test_terminal_overview_matches_reasoning_summary():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_terminal_overview_matches_case_summary_evidence():
    (
        case,
        workflow,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    overview = case_summary.reasoning_summary.overview

    assert overview["findings"] == case_summary.findings
    assert overview["root_causes"] == case_summary.root_causes
    assert (
        overview["recommendations"]
        == case_summary.recommendations
    )


def test_terminal_consistency_survives_repeated_reads():
    (
        case,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.extend(["finding-1", "finding-2"])
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    resolve_workflow(workflow)

    first = case_summary.reasoning_summary.overview
    second = case_summary.reasoning_summary.overview
    third = reasoning_summary.overview

    assert first == second
    assert second == third

    assert first["finding_count"] == 2
    assert first["root_cause_count"] == 1
    assert first["recommendation_count"] == 1