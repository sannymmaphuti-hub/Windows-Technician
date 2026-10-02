from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary, workflow, history


def test_recovery_history_remains_after_resolution():
    summary, workflow, history = create_summary()

    workflow.start_investigation()
    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.cycle_history.cycle_count == 2
    assert summary.cycle_history.latest_cycle is recovery_cycle


def test_latest_cycle_outcome_is_resolved():
    summary, workflow, history = create_summary()

    workflow.start_investigation()
    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.cycle_history.latest_cycle.outcome == "RESOLVED"


def test_recovery_history_remains_after_escalation():
    summary, workflow, history = create_summary()

    workflow.start_investigation()
    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.escalate()

    assert summary.cycle_history.cycle_count == 2
    assert summary.cycle_history.latest_cycle is recovery_cycle


def test_latest_cycle_outcome_is_escalated():
    summary, workflow, history = create_summary()

    workflow.start_investigation()
    recovery_cycle = history.latest_cycle.start_recovery_cycle()
    history.record_cycle(recovery_cycle)

    workflow.escalate()

    assert summary.cycle_history.latest_cycle.outcome == "ESCALATED"