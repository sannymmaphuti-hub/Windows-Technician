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

    return (
        case,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    )


def test_case_summary_exposes_same_reasoning_summary():
    (
        _,
        _,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert case_summary.reasoning_summary is reasoning_summary


def test_reasoning_summary_remains_live_through_case_summary():
    (
        case,
        _,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    case.findings.append("new-finding")

    exposed_summary = case_summary.reasoning_summary

    assert exposed_summary is reasoning_summary
    assert exposed_summary.findings == ["new-finding"]
    assert exposed_summary.finding_count == 1


def test_case_summary_does_not_replace_reasoning_identity():
    (
        _,
        workflow,
        _,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    assert (
        case_summary.reasoning_summary.workflow
        is workflow
    )


def test_case_summary_reasoning_identity_remains_stable():
    (
        _,
        workflow,
        history,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    original_case_id = reasoning_summary.case_id
    original_workflow_id = reasoning_summary.workflow_id

    workflow.start_investigation()

    recovery_cycle = (
        history.latest_cycle.start_recovery_cycle()
    )
    history.record_cycle(recovery_cycle)

    assert case_summary.reasoning_summary is reasoning_summary
    assert (
        case_summary.reasoning_summary.case_id
        == original_case_id
    )
    assert (
        case_summary.reasoning_summary.workflow_id
        == original_workflow_id
    )