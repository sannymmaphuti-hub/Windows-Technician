import pytest

from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_case(case_id="decision-workflow-integration-001"):
    return type(
        "Case",
        (),
        {
            "case_id": case_id,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()


def build_workflow(case_id="decision-workflow-integration-001"):
    return TechnicianWorkflow(build_case(case_id))


def build_summary(case_id="decision-workflow-integration-001"):
    workflow = build_workflow(case_id)
    summary = TechnicianCaseSummary(workflow)
    return workflow, summary


def build_recommendation(
    recommendation_type="MEMORY_REVIEW",
    category="MEMORY",
    priority="HIGH",
    description="Review high memory usage.",
    rationale="Memory pressure requires technician review.",
):
    return Recommendation(
        recommendation_type=recommendation_type,
        category=category,
        priority=priority,
        description=description,
        rationale=rationale,
    )


def build_decision(
    workflow,
    decision_type=TechnicianDecisionType.ACCEPT,
    recommendation=None,
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


def complete_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_accept_decision_does_not_start_investigation():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_reject_decision_does_not_start_investigation():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
    )
    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_defer_decision_does_not_change_workflow():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
    )
    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_investigate_further_decision_does_not_change_workflow():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.INVESTIGATE_FURTHER,
    )
    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_escalate_decision_does_not_escalate_workflow():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ESCALATE,
    )
    summary.set_decision(decision)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.state is not WorkflowState.ESCALATED
    assert workflow.history == []


def test_workflow_can_progress_after_accept_decision():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.workflow_state is WorkflowState.INVESTIGATING
    assert summary.decision is decision


def test_workflow_can_progress_after_reject_decision():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
    )
    summary.set_decision(decision)

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision


def test_workflow_can_progress_after_defer_decision():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
    )
    summary.set_decision(decision)

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision


def test_workflow_can_progress_after_investigate_further_decision():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.INVESTIGATE_FURTHER,
    )
    summary.set_decision(decision)

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision


def test_escalate_decision_can_coexist_with_non_escalated_workflow():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ESCALATE,
    )
    summary.set_decision(decision)

    assert decision.decision_type is TechnicianDecisionType.ESCALATE
    assert workflow.state is WorkflowState.OPEN
    assert workflow.state is not WorkflowState.ESCALATED


def test_explicit_workflow_escalation_is_separate_from_escalate_decision():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ESCALATE,
    )
    summary.set_decision(decision)

    workflow.escalate()

    assert decision.decision_type is TechnicianDecisionType.ESCALATE
    assert workflow.state is WorkflowState.ESCALATED
    assert summary.workflow_state is WorkflowState.ESCALATED


def test_workflow_escalation_does_not_create_decision():
    workflow, summary = build_summary()

    workflow.escalate()

    assert summary.decision is None


def test_workflow_progression_does_not_create_decision():
    workflow, summary = build_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert summary.decision is None


def test_workflow_history_contains_only_workflow_transitions():
    workflow, summary = build_summary()

    decision = build_decision(workflow)
    summary.set_decision(decision)

    assert workflow.history == []

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert len(workflow.history) == 2
    assert workflow.history[0] == (
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
    )
    assert workflow.history[1] == (
        WorkflowState.INVESTIGATING,
        WorkflowState.DIAGNOSED,
    )


def test_decision_survives_full_workflow_progression():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    complete_workflow(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert summary.decision is decision
    assert summary.decision.workflow is workflow


def test_decision_survives_workflow_reopen():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert decision.workflow is workflow


def test_decision_identity_remains_stable_during_workflow_progression():
    workflow, summary = build_summary()

    decision = build_decision(workflow)
    summary.set_decision(decision)

    decision_id = decision.decision_id

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.decision.decision_id == decision_id


def test_decision_timestamp_remains_stable_during_workflow_progression():
    workflow, summary = build_summary()

    decision = build_decision(workflow)
    summary.set_decision(decision)

    created_at = decision.created_at

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.decision.created_at == created_at


def test_replacing_decision_does_not_change_current_workflow_state():
    workflow, summary = build_summary()

    first = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(first)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    second = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
    )
    summary.set_decision(second)

    assert workflow.state is WorkflowState.DIAGNOSED
    assert summary.workflow_state is WorkflowState.DIAGNOSED
    assert summary.decision is second


def test_replacing_decision_does_not_modify_previous_decision():
    workflow, summary = build_summary()

    first = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Proceed.",
    )
    second = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
        notes="Do not proceed.",
    )

    summary.set_decision(first)
    summary.set_decision(second)

    assert first.decision_type is TechnicianDecisionType.ACCEPT
    assert first.notes == "Proceed."
    assert second.decision_type is TechnicianDecisionType.REJECT
    assert second.notes == "Do not proceed."


def test_decision_and_workflow_have_independent_terminal_concepts():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ESCALATE,
    )
    summary.set_decision(decision)

    assert decision.decision_type is TechnicianDecisionType.ESCALATE
    assert not summary.is_terminal

    workflow.escalate()

    assert summary.is_terminal
    assert workflow.state is WorkflowState.ESCALATED
    assert summary.decision is decision


def test_resolved_workflow_does_not_change_decision_type():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    complete_workflow(workflow)

    assert decision.decision_type is TechnicianDecisionType.ACCEPT


def test_decision_does_not_control_reopen_behavior():
    workflow, summary = build_summary()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
    )
    summary.set_decision(decision)

    complete_workflow(workflow)
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.decision is decision
    assert decision.decision_type is TechnicianDecisionType.REJECT


def test_decision_workflow_binding_remains_exact():
    first_workflow, first_summary = build_summary(
        "workflow-one",
    )
    second_workflow, second_summary = build_summary(
        "workflow-two",
    )

    first_decision = build_decision(first_workflow)
    second_decision = build_decision(second_workflow)

    first_summary.set_decision(first_decision)
    second_summary.set_decision(second_decision)

    assert first_decision.workflow is first_workflow
    assert second_decision.workflow is second_workflow
    assert first_decision.workflow is not second_workflow
    assert second_decision.workflow is not first_workflow


def test_decision_on_one_workflow_does_not_affect_another():
    first_workflow, first_summary = build_summary(
        "workflow-one",
    )
    second_workflow, second_summary = build_summary(
        "workflow-two",
    )

    first_decision = build_decision(
        first_workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    first_summary.set_decision(first_decision)

    first_workflow.start_investigation()

    assert first_workflow.state is WorkflowState.INVESTIGATING
    assert second_workflow.state is WorkflowState.OPEN
    assert second_summary.decision is None


def test_case_summary_tracks_workflow_and_decision_together():
    workflow, summary = build_summary()

    recommendation = build_recommendation()
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Technician approved the recommendation.",
    )

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert summary.workflow is workflow
    assert summary.workflow_state is WorkflowState.ACTION_REQUIRED
    assert summary.decision is decision
    assert summary.decision.recommendation is recommendation
    assert summary.decision.workflow is workflow


def test_complete_integration_preserves_separation():
    workflow, summary = build_summary()

    recommendation = build_recommendation(
        recommendation_type="MEMORY_REVIEW",
        priority="CRITICAL",
        description="Review critical memory pressure.",
        rationale="Critical memory pressure requires technician review.",
    )

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Proceed after technician review.",
    )

    summary.set_decision(decision)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert summary.is_terminal

    assert summary.workflow is workflow
    assert summary.decision is decision
    assert summary.decision.workflow is workflow
    assert summary.decision.recommendation is recommendation

    assert workflow.history == [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
        (WorkflowState.DIAGNOSED, WorkflowState.ACTION_REQUIRED),
        (WorkflowState.ACTION_REQUIRED, WorkflowState.REMEDIATING),
        (WorkflowState.REMEDIATING, WorkflowState.VERIFYING),
        (WorkflowState.VERIFYING, WorkflowState.RESOLVED),
    ]