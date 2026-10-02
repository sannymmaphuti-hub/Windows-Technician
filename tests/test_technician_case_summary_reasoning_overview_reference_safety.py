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

    return case, workflow, history, reasoning_summary, case_summary


def test_overview_does_not_expose_workflow_reference():
    (
        _,
        workflow,
        _,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert workflow not in overview.values()
    assert "workflow" not in overview


def test_overview_does_not_expose_case_reference():
    (
        case,
        _,
        _,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert case not in overview.values()
    assert "case" not in overview


def test_overview_does_not_expose_cycle_history_reference():
    (
        _,
        _,
        history,
        _,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert history not in overview.values()
    assert "cycle_history" not in overview


def test_overview_contains_only_reasoning_data():
    (
        _,
        _,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert set(overview.keys()) == {
        "finding_count",
        "correlation_count",
        "root_cause_count",
        "recommendation_count",
        "findings",
        "correlations",
        "root_causes",
        "recommendations",
    }

    assert overview == reasoning_summary.overview