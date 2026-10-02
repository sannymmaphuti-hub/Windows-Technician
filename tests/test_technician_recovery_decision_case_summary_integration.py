import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(
        TechnicianReasoningSummary(workflow, history)
    )
    return summary


def build_recommendation():
    return Recommendation(
        "test-recommendation",
        "Test recommendation",
        "MEDIUM",
        "Test recommendation description",
        "Test recommendation rationale",
    )


def build_decision(workflow, decision_type, notes=""):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=decision_type,
        notes=notes,
    )


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def complete_lifecycle(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def complete_reopened_lifecycle(workflow):
    workflow.reopen()
    complete_lifecycle(workflow)


def test_recovery_history_and_decision_coexist_in_case_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = record_cycle(workflow, history, 1)
    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        notes="Proceed with recovery.",
    )

    summary.set_decision(decision)

    assert summary.reasoning_summary.cycle_history is history
    assert summary.reasoning_summary.cycle_history.latest_cycle is cycle
    assert summary.decision is decision


def test_setting_decision_does_not_replace_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )
    summary.set_decision(decision)

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history is history
    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second
    assert summary.decision is decision


def test_recovery_history_does_not_mutate_decision():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        notes="Wait for additional evidence.",
    )
    summary.set_decision(decision)

    original_decision_id = decision.decision_id
    original_decision_type = decision.decision_type
    original_notes = decision.notes
    original_recommendation = decision.recommendation

    record_cycle(workflow, history, 1)
    record_cycle(workflow, history, 2)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    assert summary.decision is decision
    assert decision.decision_id == original_decision_id
    assert decision.decision_type is original_decision_type
    assert decision.notes == original_notes
    assert decision.recommendation is original_recommendation


def test_workflow_activity_preserves_both_recovery_history_and_decision():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
        notes="Do not apply the recommendation yet.",
    )
    summary.set_decision(decision)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    for _ in range(4):
        complete_reopened_lifecycle(workflow)

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycles[1] is first
    assert cycle_history.cycle_count == 2
    assert summary.decision is decision
    assert workflow.state.name == "RESOLVED"


def test_reopening_preserves_recovery_history_and_case_decision():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
        notes="Escalate for technician review.",
    )
    summary.set_decision(decision)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    workflow.reopen()

    second = record_cycle(workflow, history, 2)

    assert workflow.state.name == "INVESTIGATING"
    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history.cycles[1] is first
    assert summary.reasoning_summary.cycle_history.cycles[2] is second


def test_multiple_decisions_do_not_duplicate_or_replace_recovery_cycles():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    decisions = [
        build_decision(workflow, TechnicianDecisionType.ACCEPT),
        build_decision(workflow, TechnicianDecisionType.REJECT),
        build_decision(workflow, TechnicianDecisionType.DEFER),
        build_decision(
            workflow,
            TechnicianDecisionType.INVESTIGATE_FURTHER,
        ),
        build_decision(workflow, TechnicianDecisionType.ESCALATE),
    ]

    for decision in decisions:
        summary.set_decision(decision)
        assert summary.decision is decision

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycle_count == 3
    assert cycle_history.cycles[1] is first
    assert cycle_history.cycles[2] is second


def test_case_summary_keeps_decision_separate_from_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = record_cycle(workflow, history, 1)
    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is history
    assert summary.decision is not summary.reasoning_summary.cycle_history
    assert summary.decision is not cycle


def test_failed_workflow_operations_preserve_decision_and_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    first = record_cycle(workflow, history, 1)
    second = record_cycle(workflow, history, 2)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
        notes="Maintain current state after failed operation.",
    )
    summary.set_decision(decision)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history.cycles[1] is first
    assert summary.reasoning_summary.cycle_history.cycles[2] is second
    assert summary.reasoning_summary.cycle_history.cycle_count == 3


def test_decision_and_recovery_history_survive_escalation():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycles = [
        record_cycle(workflow, history, 1),
        record_cycle(workflow, history, 2),
        record_cycle(workflow, history, 3),
    ]

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
        notes="Escalation required.",
    )
    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.escalate()

    assert workflow.state.name == "ESCALATED"
    assert summary.decision is decision

    cycle_history = summary.reasoning_summary.cycle_history

    assert cycle_history.cycle_count == 4

    for index, cycle in enumerate(cycles, start=1):
        assert cycle_history.cycles[index] is cycle


def test_long_sequence_preserves_decision_and_complete_recovery_timeline():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        notes="Continue investigation across recovery cycles.",
    )
    summary.set_decision(decision)

    workflow.start_investigation()
    complete_lifecycle(workflow)

    expected_cycles = []

    for cycle_number in range(1, 11):
        expected_cycles.append(
            record_cycle(workflow, history, cycle_number)
        )

        if cycle_number < 10:
            complete_reopened_lifecycle(workflow)

    cycle_history = summary.reasoning_summary.cycle_history

    assert summary.decision is decision
    assert cycle_history is history
    assert cycle_history.cycle_count == 11

    for index, expected_cycle in enumerate(expected_cycles, start=1):
        assert cycle_history.cycles[index] is expected_cycle

    assert [cycle.cycle_number for cycle in cycle_history.cycles] == list(
        range(11)
    )
    