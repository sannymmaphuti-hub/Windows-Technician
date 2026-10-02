from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_workflow():
    case = type(
        "Case",
        (),
        {
            "case_id": "decision-lifecycle-001",
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()

    return TechnicianWorkflow(case)


def build_recommendation(
    recommendation_type="TEST_RECOMMENDATION",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category="MEMORY",
        priority="HIGH",
        description="Review high memory usage.",
        rationale="Memory pressure requires technician review.",
    )


def build_decision(
    workflow,
    recommendation=None,
    decision_type=TechnicianDecisionType.ACCEPT,
    notes="Technician decision recorded.",
):
    if recommendation is None:
        recommendation = build_recommendation()

    return TechnicianDecision(
        workflow=workflow,
        recommendation=recommendation,
        decision_type=decision_type,
        notes=notes,
    )


def build_summary():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)
    return workflow, summary


def complete_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_decision_is_available_across_complete_lifecycle():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert summary.decision is decision
    assert summary.decision.workflow is workflow


def test_decision_identity_survives_resolution():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)

    assert summary.decision is decision
    assert summary.decision.decision_id == decision.decision_id


def test_decision_identity_survives_reopen():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert summary.decision.decision_id == decision.decision_id


def test_recommendation_identity_survives_resolution_and_reopen():
    workflow, summary = build_summary()
    recommendation = build_recommendation()
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert summary.decision.recommendation is recommendation


def test_decision_does_not_appear_as_case_evidence():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_decision_does_not_change_evidence_after_resolution():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_decision_does_not_change_evidence_after_reopen():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_decision_does_not_change_reasoning_summary_counts():
    workflow, summary = build_summary()

    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )

    summary.set_reasoning_summary(reasoning)

    before = reasoning.overview

    decision = build_decision(workflow)
    summary.set_decision(decision)

    after = reasoning.overview

    assert before["finding_count"] == after["finding_count"]
    assert before["correlation_count"] == after["correlation_count"]
    assert before["root_cause_count"] == after["root_cause_count"]
    assert before["recommendation_count"] == after["recommendation_count"]


def test_decision_does_not_enter_reasoning_overview():
    workflow, summary = build_summary()

    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )

    summary.set_reasoning_summary(reasoning)

    decision = build_decision(workflow)
    summary.set_decision(decision)

    overview = reasoning.overview

    assert "decision" not in overview
    assert "decision_id" not in overview
    assert "decision_type" not in overview


def test_workflow_history_remains_separate_from_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert workflow.history == []

    workflow.start_investigation()

    assert len(workflow.history) == 1
    assert summary.decision is decision


def test_decision_does_not_create_workflow_history():
    workflow, summary = build_summary()

    before = list(workflow.history)

    decision = build_decision(workflow)
    summary.set_decision(decision)

    assert workflow.history == before
    assert workflow.history == []


def test_resolution_history_does_not_replace_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)

    assert len(workflow.history) == 6
    assert summary.decision is decision


def test_reopen_history_does_not_replace_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)
    history_before_reopen = list(workflow.history)

    workflow.reopen()

    assert len(workflow.history) == len(history_before_reopen) + 1
    assert summary.decision is decision


def test_decision_remains_bound_to_original_workflow_after_reopen():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert decision.workflow is workflow
    assert summary.decision.workflow is workflow
    assert summary.workflow is workflow


def test_replacing_decision_after_reopen_does_not_duplicate_evidence():
    workflow, summary = build_summary()
    first_decision = build_decision(
        workflow,
        notes="First decision.",
    )

    summary.set_decision(first_decision)

    complete_workflow(workflow)
    workflow.reopen()

    second_decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.INVESTIGATE_FURTHER,
        notes="Further investigation required.",
    )

    summary.set_decision(second_decision)

    assert summary.decision is second_decision
    assert summary.decision is not first_decision

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_replacing_decision_does_not_modify_previous_decision():
    workflow, summary = build_summary()

    first = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Accepted.",
    )

    second = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
        notes="Deferred.",
    )

    summary.set_decision(first)
    summary.set_decision(second)

    assert first.decision_type is TechnicianDecisionType.ACCEPT
    assert first.notes == "Accepted."

    assert second.decision_type is TechnicianDecisionType.DEFER
    assert second.notes == "Deferred."


def test_decision_created_at_remains_stable():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    created_at = decision.created_at

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert summary.decision.created_at == created_at


def test_decision_id_remains_stable_through_lifecycle():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    decision_id = decision.decision_id

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert summary.decision.decision_id == decision_id


def test_case_summary_remains_live_while_decision_remains_stable():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    assert summary.workflow_state is WorkflowState.OPEN
    assert summary.decision is decision

    workflow.start_investigation()

    assert summary.workflow_state is WorkflowState.INVESTIGATING
    assert summary.decision is decision

    workflow.mark_diagnosed()

    assert summary.workflow_state is WorkflowState.DIAGNOSED
    assert summary.decision is decision


def test_terminal_state_does_not_erase_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)

    assert summary.is_terminal
    assert summary.closure is None
    assert summary.decision is decision


def test_reopen_does_not_erase_decision():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert not summary.is_terminal
    assert summary.decision is decision


def test_decision_and_recovery_history_remain_separate():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    cycle_history = TechnicianRecoveryCycleHistory(workflow)

    summary.set_decision(decision)

    assert summary.decision is decision
    assert cycle_history.workflow is workflow
    assert summary.decision is not cycle_history


def test_decision_does_not_create_recovery_cycles():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    cycle_history = TechnicianRecoveryCycleHistory(workflow)

    summary.set_decision(decision)

    assert cycle_history.cycle_count == 1
    assert cycle_history.latest_cycle.is_original


def test_full_lifecycle_preserves_decision_and_recovery_separation():
    workflow, summary = build_summary()
    decision = build_decision(workflow)

    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning = TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )

    summary.set_reasoning_summary(reasoning)
    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert summary.decision is decision
    assert summary.reasoning_summary is reasoning
    assert summary.workflow is workflow
    assert summary.decision.workflow is workflow
    assert summary.reasoning_summary.workflow is workflow
    assert cycle_history.workflow is workflow
    assert cycle_history.cycle_count == 1