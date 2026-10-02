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


def test_case_summary_reasoning_overview_matches_summary():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert (
        case_summary.reasoning_summary.overview
        == reasoning_summary.overview
    )


def test_case_summary_reasoning_overview_is_current():
    case, _, case_summary = create_summaries()

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    overview = case_summary.reasoning_summary.overview

    assert overview["finding_count"] == 1
    assert overview["root_cause_count"] == 1
    assert overview["findings"] == ["finding"]
    assert overview["root_causes"] == ["root-cause"]


def test_case_summary_does_not_create_duplicate_overview():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    first = case_summary.reasoning_summary.overview
    second = reasoning_summary.overview

    assert first == second