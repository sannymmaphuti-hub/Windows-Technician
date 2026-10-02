import pytest

from engine.recommendation import Recommendation
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_case(case_id="decision-contract-case"):
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


def build_workflow(case_id="decision-contract-case"):
    return TechnicianWorkflow(build_case(case_id))


def build_recommendation(
    recommendation_type="TEST_RECOMMENDATION",
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


def test_valid_decision_is_created():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    assert isinstance(decision, TechnicianDecision)


def test_decision_requires_valid_workflow():
    recommendation = build_recommendation()

    with pytest.raises(ValueError, match="TechnicianDecision requires a TechnicianWorkflow"):
        TechnicianDecision(
            workflow=None,
            recommendation=recommendation,
            decision_type=TechnicianDecisionType.ACCEPT,
        )


def test_decision_requires_valid_recommendation():
    workflow = build_workflow()

    with pytest.raises(ValueError, match="TechnicianDecision requires a Recommendation"):
        TechnicianDecision(
            workflow=workflow,
            recommendation=None,
            decision_type=TechnicianDecisionType.ACCEPT,
        )


def test_decision_requires_valid_decision_type():
    workflow = build_workflow()
    recommendation = build_recommendation()

    with pytest.raises(ValueError, match="TechnicianDecision requires a valid decision type"):
        TechnicianDecision(
            workflow=workflow,
            recommendation=recommendation,
            decision_type="ACCEPT",
        )


def test_decision_requires_string_notes():
    workflow = build_workflow()
    recommendation = build_recommendation()

    with pytest.raises(ValueError, match="TechnicianDecision notes must be a string"):
        TechnicianDecision(
            workflow=workflow,
            recommendation=recommendation,
            decision_type=TechnicianDecisionType.ACCEPT,
            notes=None,
        )


def test_decision_preserves_exact_workflow_identity():
    workflow = build_workflow()
    decision = build_decision(workflow)

    assert decision.workflow is workflow


def test_decision_preserves_exact_recommendation_identity():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    assert decision.recommendation is recommendation


def test_decision_preserves_exact_decision_type():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.DEFER,
    )

    assert decision.decision_type is TechnicianDecisionType.DEFER


def test_decision_preserves_exact_notes():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        notes="Investigate before proceeding.",
    )

    assert decision.notes == "Investigate before proceeding."


@pytest.mark.parametrize(
    "decision_type",
    [
        TechnicianDecisionType.ACCEPT,
        TechnicianDecisionType.REJECT,
        TechnicianDecisionType.DEFER,
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        TechnicianDecisionType.ESCALATE,
    ],
)
def test_all_decision_types_are_valid(decision_type):
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        decision_type=decision_type,
    )

    assert decision.decision_type is decision_type


def test_decision_has_unique_identity():
    workflow = build_workflow()

    first = build_decision(workflow)
    second = build_decision(workflow)

    assert first.decision_id != second.decision_id


def test_decision_timestamp_is_created():
    workflow = build_workflow()

    decision = build_decision(workflow)

    assert decision.created_at is not None


def test_decision_identity_remains_stable():
    workflow = build_workflow()

    decision = build_decision(workflow)

    decision_id = decision.decision_id

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert decision.decision_id == decision_id


def test_decision_timestamp_remains_stable():
    workflow = build_workflow()

    decision = build_decision(workflow)

    created_at = decision.created_at

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert decision.created_at == created_at


def test_decision_does_not_mutate_workflow():
    workflow = build_workflow()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []

    build_decision(workflow)

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_decision_does_not_mutate_recommendation():
    workflow = build_workflow()
    recommendation = build_recommendation()

    original = (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )

    build_decision(
        workflow,
        recommendation=recommendation,
    )

    current = (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )

    assert current == original


def test_decision_notes_are_stable_after_workflow_changes():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        notes="Keep the case under observation.",
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert decision.notes == "Keep the case under observation."


def test_decision_remains_bound_to_original_workflow():
    first_workflow = build_workflow("workflow-one")
    second_workflow = build_workflow("workflow-two")

    decision = build_decision(first_workflow)

    assert decision.workflow is first_workflow
    assert decision.workflow is not second_workflow


def test_two_decisions_on_same_workflow_remain_distinct():
    workflow = build_workflow()

    first = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Accept.",
    )

    second = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.REJECT,
        notes="Reject.",
    )

    assert first is not second
    assert first.decision_id != second.decision_id
    assert first.decision_type is TechnicianDecisionType.ACCEPT
    assert second.decision_type is TechnicianDecisionType.REJECT
    assert first.notes == "Accept."
    assert second.notes == "Reject."


def test_decision_remains_stable_when_workflow_is_reopened():
    workflow = build_workflow()

    decision = build_decision(workflow)

    decision_id = decision.decision_id
    created_at = decision.created_at

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert decision.workflow is workflow
    assert decision.decision_id == decision_id
    assert decision.created_at == created_at


def test_decision_does_not_authorize_remediation():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    assert decision.decision_type is TechnicianDecisionType.ACCEPT

    # TechnicianDecision contains intent only.
    # It has no remediation authorization state.
    assert not hasattr(decision, "authorization_status")
    assert not hasattr(decision, "execution_status")


def test_decision_does_not_execute_remediation():
    workflow = build_workflow()

    decision = build_decision(
        workflow,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_decision_contract_preserves_all_core_fields():
    workflow = build_workflow()
    recommendation = build_recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="CRITICAL",
        description="Review critical memory pressure.",
        rationale="Available memory is critically constrained.",
    )

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ESCALATE,
        notes="Escalate to senior technician.",
    )

    assert decision.workflow is workflow
    assert decision.recommendation is recommendation
    assert decision.decision_type is TechnicianDecisionType.ESCALATE
    assert decision.notes == "Escalate to senior technician."
    assert isinstance(decision.decision_id, str)
    assert decision.created_at is not None