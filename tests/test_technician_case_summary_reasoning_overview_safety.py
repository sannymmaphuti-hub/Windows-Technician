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


def test_case_summary_returns_same_reasoning_summary_instance():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert case_summary.reasoning_summary is reasoning_summary


def test_case_summary_overview_does_not_replace_reasoning_summary():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    assert case_summary.reasoning_summary is reasoning_summary
    assert overview == reasoning_summary.overview


def test_case_summary_overview_collections_are_isolated():
    case, _, case_summary = create_summaries()

    case.findings.append("finding")

    overview = case_summary.reasoning_summary.overview

    overview["findings"].append("fake")

    assert case.findings == ["finding"]
    assert case_summary.reasoning_summary.findings == ["finding"]


def test_case_summary_overview_does_not_mutate_case_state():
    case, _, case_summary = create_summaries()

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    before = (
        list(case.findings),
        list(case.root_causes),
    )

    overview = case_summary.reasoning_summary.overview

    overview["findings"].clear()
    overview["root_causes"].clear()

    after = (
        list(case.findings),
        list(case.root_causes),
    )

    assert after == before