from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow
from tests.test_technician_evidence_findings_summary import history


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def build_decision(
    workflow,
    decision_type=TechnicianDecisionType.ACCEPT,
    notes="Recommendation decision recorded.",
):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=decision_type,
        notes=notes,
    )


def prepare_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()


def record_recovery_cycle(workflow, history, cycle_number=1):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def test_recovery_cycle_does_not_mutate_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(workflow)

    decision_id_before = decision.decision_id
    created_at_before = decision.created_at
    recommendation_before = decision.recommendation
    decision_type_before = decision.decision_type
    notes_before = decision.notes

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_id == decision_id_before
    assert decision.created_at == created_at_before
    assert decision.recommendation is recommendation_before
    assert decision.decision_type is decision_type_before
    assert decision.notes == notes_before


def test_recovery_cycle_preserves_decision_workflow_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(workflow)

    cycle = record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.workflow is workflow
    assert cycle.workflow is workflow


def test_recovery_cycle_does_not_become_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(workflow)

    cycle = record_recovery_cycle(
        workflow,
        history,
    )

    assert cycle is not decision
    assert isinstance(decision, TechnicianDecision)
    assert isinstance(cycle, TechnicianRecoveryCycle)


def test_recovery_cycle_preserves_accepted_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_type is TechnicianDecisionType.ACCEPT


def test_recovery_cycle_preserves_rejected_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
    )

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_type is TechnicianDecisionType.REJECT


def test_recovery_cycle_preserves_deferred_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.DEFER,
    )

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_type is TechnicianDecisionType.DEFER


def test_recovery_cycle_preserves_investigate_further_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
    )

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_type is TechnicianDecisionType.INVESTIGATE_FURTHER


def test_recovery_cycle_preserves_escalation_decision():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(
        workflow,
        TechnicianDecisionType.ESCALATE,
    )

    record_recovery_cycle(
        workflow,
        history,
    )

    assert decision.decision_type is TechnicianDecisionType.ESCALATE


def test_recovery_cycle_does_not_change_workflow_state():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    state_before = workflow.state

    build_decision(workflow)

    record_recovery_cycle(
        workflow,
        history,
    )

    assert workflow.state is state_before


def test_recovery_cycle_does_not_change_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    history_before = list(workflow.history)

    build_decision(workflow)

    record_recovery_cycle(
        workflow,
        history,
    )

    assert workflow.history == history_before


def test_multiple_recovery_cycles_preserve_decision_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(workflow)

    cycles = [
        record_recovery_cycle(
            workflow,
            history,
            cycle_number=1,
        ),
        record_recovery_cycle(
            workflow,
            history,
            cycle_number=2,
        ),
        record_recovery_cycle(
            workflow,
            history,
            cycle_number=3,
        ),
    ]

    assert decision.workflow is workflow
    assert history.cycles[1:] == cycles
    assert len(history.cycles) == 4
    assert all(cycle.workflow is workflow for cycle in cycles)


def test_multiple_decisions_can_coexist_with_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
        notes="First recommendation rejected.",
    )

    cycle = record_recovery_cycle(
        workflow,
        history,
    )

    second_decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
        notes="Follow-up recommendation accepted.",
    )

    assert first_decision.workflow is workflow
    assert second_decision.workflow is workflow
    assert first_decision.decision_id != second_decision.decision_id
    assert history.cycles[-1] is cycle
    assert len(history.cycles) == 2


def test_recovery_history_is_separate_from_decision_objects():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    decision = build_decision(workflow)
    cycle = record_recovery_cycle(
        workflow,
        history,
    )

    assert decision is not cycle
    assert history.cycles[-1] is cycle
    assert len(history.cycles) == 2


def test_recovery_cycles_remain_historical_when_decision_changes():
    workflow = build_workflow()
    history = build_history(workflow)

    prepare_workflow(workflow)

    first_decision = build_decision(
        workflow,
        TechnicianDecisionType.REJECT,
    )

    first_cycle = record_recovery_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    second_decision = build_decision(
        workflow,
        TechnicianDecisionType.ACCEPT,
    )

    second_cycle = record_recovery_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    assert first_decision.decision_type is TechnicianDecisionType.REJECT
    assert second_decision.decision_type is TechnicianDecisionType.ACCEPT
    assert history.cycles[1:] == [
        first_cycle,
        second_cycle,
        ]
    assert len(history.cycles) == 3