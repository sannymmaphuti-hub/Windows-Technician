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

    return case, workflow, reasoning_summary, case_summary


def test_overview_is_unchanged_when_workflow_enters_investigation():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    before = case_summary.reasoning_summary.overview

    workflow.start_investigation()

    after = case_summary.reasoning_summary.overview

    assert after == before
    assert after == reasoning_summary.overview


def test_overview_is_unchanged_when_workflow_becomes_diagnosed():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()

    before = case_summary.reasoning_summary.overview

    workflow.mark_diagnosed()

    after = case_summary.reasoning_summary.overview

    assert after == before
    assert after == reasoning_summary.overview


def test_overview_is_unchanged_when_workflow_reaches_action_required():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    before = case_summary.reasoning_summary.overview

    workflow.require_action()

    after = case_summary.reasoning_summary.overview

    assert after == before
    assert after == reasoning_summary.overview


def test_overview_is_unchanged_when_workflow_reaches_terminal_state():
    (
        _,
        workflow,
        reasoning_summary,
        case_summary,
    ) = create_summaries()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    before = case_summary.reasoning_summary.overview

    workflow.resolve()

    after = case_summary.reasoning_summary.overview

    assert workflow.is_terminal is True
    assert after == before
    assert after == reasoning_summary.overview