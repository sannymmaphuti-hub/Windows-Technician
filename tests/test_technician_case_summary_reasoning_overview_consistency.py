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

    return case, reasoning_summary, case_summary


def test_empty_overviews_are_consistent():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert case_summary.reasoning_summary.overview == {
        "finding_count": 0,
        "correlation_count": 0,
        "root_cause_count": 0,
        "recommendation_count": 0,
        "findings": [],
        "correlations": [],
        "root_causes": [],
        "recommendations": [],
    }

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_each_overview_count_matches_its_collection():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.extend(["f1", "f2"])
    case.correlations.append("c1")
    case.root_causes.extend(["r1", "r2", "r3"])
    case.recommendations.append("rec1")

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


def test_case_summary_and_reasoning_summary_remain_equal():
    (
        case,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_consistency_survives_incremental_evidence_changes():
    (
        case,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    case.correlations.append("correlation")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    case.root_causes.append("root-cause")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )

    case.recommendations.append("recommendation")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )