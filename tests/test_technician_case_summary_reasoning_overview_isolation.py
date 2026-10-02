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


def test_repeated_overview_reads_are_distinct_dictionaries():
    (
        _,
        _,
        case_summary,
    ) = create_summaries()

    first = case_summary.reasoning_summary.overview
    second = case_summary.reasoning_summary.overview

    assert first is not second
    assert first == second


def test_repeated_overview_reads_have_independent_collections():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")

    first = case_summary.reasoning_summary.overview
    second = case_summary.reasoning_summary.overview

    assert first["findings"] is not second["findings"]

    first["findings"].append("fake")

    assert second["findings"] == ["finding"]


def test_mutating_one_overview_does_not_affect_later_reads():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.root_causes.append("root-cause")
    case.recommendations.append("recommendation")

    first = case_summary.reasoning_summary.overview

    first["root_causes"].clear()
    first["recommendations"].clear()
    first["root_cause_count"] = 999
    first["recommendation_count"] = 999

    second = case_summary.reasoning_summary.overview

    assert second["root_causes"] == ["root-cause"]
    assert second["recommendations"] == ["recommendation"]
    assert second["root_cause_count"] == 1
    assert second["recommendation_count"] == 1


def test_isolation_does_not_break_live_synchronization():
    (
        case,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    first = case_summary.reasoning_summary.overview
    first["findings"].append("fake")

    case.findings.append("real-finding")

    second = case_summary.reasoning_summary.overview

    assert second["findings"] == ["real-finding"]
    assert second["finding_count"] == 1
    assert second == reasoning_summary.overview