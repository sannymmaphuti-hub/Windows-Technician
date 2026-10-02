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


def test_overview_dictionary_mutation_does_not_change_summary():
    (
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    overview = case_summary.reasoning_summary.overview

    overview["finding_count"] = 999
    overview["root_cause_count"] = 999

    assert reasoning_summary.finding_count == 0
    assert reasoning_summary.root_cause_count == 0

    assert (
        case_summary.reasoning_summary.overview["finding_count"]
        == 0
    )
    assert (
        case_summary.reasoning_summary.overview["root_cause_count"]
        == 0
    )


def test_overview_collection_mutation_does_not_change_summary():
    (
        case,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.root_causes.append("root-cause")

    overview = case_summary.reasoning_summary.overview

    overview["findings"].append("fake-finding")
    overview["root_causes"].append("fake-root-cause")

    assert reasoning_summary.findings == ["finding"]
    assert reasoning_summary.root_causes == ["root-cause"]

    assert case.findings == ["finding"]
    assert case.root_causes == ["root-cause"]


def test_retrieving_overview_again_returns_clean_data():
    (
        case,
        _,
        case_summary,
    ) = create_summaries()

    case.findings.append("finding")
    case.recommendations.append("recommendation")

    first = case_summary.reasoning_summary.overview

    first["findings"].clear()
    first["recommendations"].clear()

    second = case_summary.reasoning_summary.overview

    assert second["findings"] == ["finding"]
    assert second["recommendations"] == ["recommendation"]
    assert second["finding_count"] == 1
    assert second["recommendation_count"] == 1


def test_overview_mutation_cannot_change_case_summary_identity():
    (
        case,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    original_case_id = case_summary.case_id
    original_workflow_id = case_summary.workflow_id

    overview = case_summary.reasoning_summary.overview

    overview["finding_count"] = 100
    overview["findings"].append("fake")

    assert case_summary.case_id == original_case_id
    assert case_summary.workflow_id == original_workflow_id

    assert reasoning_summary.case_id == case.case_id
    assert reasoning_summary.workflow_id == case_summary.workflow_id