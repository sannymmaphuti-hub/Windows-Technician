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


def test_overview_reflects_evidence_added_after_first_read():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    first = case_summary.reasoning_summary.overview

    assert first["finding_count"] == 0

    case.findings.append("finding")

    second = case_summary.reasoning_summary.overview

    assert second["finding_count"] == 1
    assert second["findings"] == ["finding"]


def test_overview_reflects_multiple_incremental_changes():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    first = case_summary.reasoning_summary.overview

    assert first["finding_count"] == 1

    case.findings.append("finding-2")
    case.root_causes.append("root-cause")

    second = case_summary.reasoning_summary.overview

    assert second["finding_count"] == 2
    assert second["root_cause_count"] == 1
    assert second["findings"] == [
        "finding",
        "finding-2",
    ]
    assert second["root_causes"] == [
        "root-cause",
    ]


def test_overview_tracks_all_reasoning_categories_live():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.correlations.append("correlation")
    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == 1
    assert overview["correlation_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["recommendation_count"] == 1

    assert overview["findings"] == ["finding"]
    assert overview["correlations"] == ["correlation"]
    assert overview["root_causes"] == ["root-cause"]
    assert overview["recommendations"] == [
        "recommendation",
    ]


def test_case_summary_and_reasoning_summary_stay_live_together():
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

    case.recommendations.append("recommendation")

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )