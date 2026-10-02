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


def test_empty_overview_is_explicit():
    (
        _,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == 0
    assert overview["correlation_count"] == 0
    assert overview["root_cause_count"] == 0
    assert overview["recommendation_count"] == 0

    assert overview["findings"] == []
    assert overview["correlations"] == []
    assert overview["root_causes"] == []
    assert overview["recommendations"] == []


def test_empty_overview_has_no_none_values():
    (
        _,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert all(
        value is not None
        for value in overview.values()
    )


def test_empty_overview_collections_are_independent():
    (
        _,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    overview["findings"].append("fake")
    overview["correlations"].append("fake")
    overview["root_causes"].append("fake")
    overview["recommendations"].append("fake")

    fresh = case_summary.reasoning_summary.overview

    assert fresh["findings"] == []
    assert fresh["correlations"] == []
    assert fresh["root_causes"] == []
    assert fresh["recommendations"] == []

    assert fresh["finding_count"] == 0
    assert fresh["correlation_count"] == 0
    assert fresh["root_cause_count"] == 0
    assert fresh["recommendation_count"] == 0


def test_empty_overview_matches_reasoning_summary_directly():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )