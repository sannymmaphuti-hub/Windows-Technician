import pytest

from engine.recommendation import Recommendation
from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action import RemediationAction
from engine.remediation_action_planner import RemediationActionPlanner
from engine.remediation_decision_boundary import (
    RemediationDecisionBoundary,
)
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_workflow import TechnicianWorkflow


def build_case():
    return type(
        "Case",
        (),
        {
            "case_id": "decision-remediation-integration-001",
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
    )()


def build_workflow():
    return TechnicianWorkflow(build_case())


def build_summary():
    workflow = build_workflow()
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


def build_action(recommendation):
    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    return planner.create_action(planner_input)


def test_decision_preserves_recommendation_for_remediation_boundary():
    workflow = build_workflow()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    assert decision.recommendation is recommendation


def test_high_recommendation_is_eligible_independently_of_decision():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    result = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )

    assert result.eligible is True


def test_critical_recommendation_is_eligible_independently_of_decision():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="CRITICAL")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    result = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )

    assert result.eligible is True


@pytest.mark.parametrize("priority", ["MEDIUM", "LOW"])
def test_medium_and_low_recommendations_are_not_eligible(priority):
    workflow = build_workflow()
    recommendation = build_recommendation(priority=priority)
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    result = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )

    assert result.eligible is False


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
def test_decision_type_does_not_change_remediation_eligibility(
    decision_type,
):
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=decision_type,
    )

    result = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )

    assert result.eligible is True


def test_accept_decision_does_not_create_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert not hasattr(decision, "remediation_action")


def test_reject_decision_does_not_create_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.REJECT,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert not hasattr(decision, "remediation_action")


def test_defer_decision_does_not_create_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.DEFER,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert not hasattr(decision, "remediation_action")


def test_investigate_further_decision_does_not_create_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.INVESTIGATE_FURTHER,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert not hasattr(decision, "remediation_action")


def test_escalate_decision_does_not_create_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation()

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ESCALATE,
    )
    summary.set_decision(decision)

    assert summary.decision is decision
    assert not hasattr(decision, "remediation_action")


def test_planner_can_create_action_independently_of_decision():
    recommendation = build_recommendation(priority="HIGH")

    action = build_action(recommendation)

    assert isinstance(action, RemediationAction)


def test_planner_action_starts_unauthorized():
    recommendation = build_recommendation(priority="HIGH")

    action = build_action(recommendation)

    assert action.authorization_status == "UNAUTHORIZED"


def test_planner_action_starts_not_executed():
    recommendation = build_recommendation(priority="HIGH")

    action = build_action(recommendation)

    assert action.execution_status == "NOT_EXECUTED"


def test_accept_decision_does_not_authorize_action():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    action = build_action(decision.recommendation)

    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert action.authorization_status == "UNAUTHORIZED"


def test_reject_decision_does_not_deny_or_authorize_action():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.REJECT,
    )

    action = build_action(decision.recommendation)

    assert decision.decision_type is TechnicianDecisionType.REJECT
    assert action.authorization_status == "UNAUTHORIZED"


def test_decision_and_action_remain_separate_objects():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    action = build_action(decision.recommendation)

    assert decision is not action
    assert decision.recommendation is recommendation
    assert action is not recommendation


def test_action_does_not_mutate_decision():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    action = build_action(decision.recommendation)

    original_id = decision.decision_id
    original_type = decision.decision_type
    original_notes = decision.notes

    action.authorize()

    assert decision.decision_id == original_id
    assert decision.decision_type is original_type
    assert decision.notes == original_notes


def test_action_does_not_mutate_recommendation():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")
    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    original = (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )

    action = build_action(decision.recommendation)
    action.authorize()

    current = (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )

    assert current == original


def test_explicit_authorization_is_separate_from_accept_decision():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    action = build_action(decision.recommendation)

    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_authorization_does_not_change_decision():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Approved for technician consideration.",
    )

    action = build_action(decision.recommendation)
    action.authorize()

    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert decision.notes == "Approved for technician consideration."
    assert decision.workflow is workflow


def test_replacing_decision_does_not_replace_remediation_action():
    workflow, summary = build_summary()
    recommendation = build_recommendation(priority="HIGH")

    first = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )
    summary.set_decision(first)

    action = build_action(first.recommendation)

    second = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.DEFER,
    )
    summary.set_decision(second)

    assert summary.decision is second
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remediation_action_identity_is_independent_of_decision_identity():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )
    action = build_action(decision.recommendation)

    assert decision.decision_id != action.action_id


def test_high_recommendation_can_reach_action_without_decision_side_effect():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="HIGH")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
        decision_type=TechnicianDecisionType.ACCEPT,
    )

    eligibility = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )
    action = build_action(decision.recommendation)

    assert eligibility.eligible is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_medium_recommendation_action_remains_separate_from_eligibility():
    workflow = build_workflow()
    recommendation = build_recommendation(priority="MEDIUM")

    decision = build_decision(
        workflow,
        recommendation=recommendation,
    )

    eligibility = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )
    action = build_action(decision.recommendation)

    assert eligibility.eligible is False
    assert isinstance(action, RemediationAction)
    assert action.authorization_status == "UNAUTHORIZED"


def test_full_decision_remediation_boundary_preserves_separation():
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
        notes="Technician approved review of the recommendation.",
    )

    summary.set_decision(decision)

    eligibility = RemediationDecisionBoundary().evaluate(
        decision.recommendation
    )
    action = build_action(decision.recommendation)

    assert summary.decision is decision
    assert decision.recommendation is recommendation
    assert eligibility.eligible is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert summary.decision is decision
    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert decision.notes == "Technician approved review of the recommendation."