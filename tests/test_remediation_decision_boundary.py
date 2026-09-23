from engine.recommendation import Recommendation
from engine.remediation_decision_boundary import (
    RemediationDecisionBoundary,
)
from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action_planner import (
    RemediationActionPlanner,
)


def test_high_priority_recommendation_is_eligible_for_remediation():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description=(
            "Review memory-intensive processes and close "
            "unnecessary applications."
        ),
        rationale=(
            "High-severity memory findings indicate that "
            "available memory may be under significant pressure."
        ),
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True
    assert decision.recommendation_type == "memory_review"


def test_medium_priority_recommendation_is_not_eligible_for_remediation():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory usage.",
        rationale="Memory usage requires attention.",
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False


def test_low_priority_recommendation_is_not_eligible_for_remediation():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="LOW",
        description="Review memory usage.",
        rationale="Memory usage requires attention.",
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False


def test_critical_priority_recommendation_is_eligible_for_remediation():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="CRITICAL",
        description="Review critical memory pressure.",
        rationale="Critical memory pressure requires attention.",
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True

def test_eligibility_does_not_authorize_or_execute_recommendation():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review memory usage.",
        rationale="High memory pressure requires attention.",
    )

    boundary = RemediationDecisionBoundary()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True
    assert not hasattr(decision, "authorized")
    assert not hasattr(decision, "executed")

def test_eligible_recommendation_can_enter_existing_remediation_adapter():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review memory usage.",
        rationale="High memory pressure requires attention.",
    )

    boundary = RemediationDecisionBoundary()
    adapter = RecommendationRemediationAdapter()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True

    planner_input = adapter.to_planner_input(
        recommendation
    )

    assert planner_input["recommendation"] == (
        "Review memory usage."
    )
    assert planner_input["category"] == "MEMORY"
    assert planner_input["severity"] == "WARNING"

def test_ineligible_recommendation_does_not_enter_remediation_adapter():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory usage.",
        rationale="Memory usage requires attention.",
    )

    boundary = RemediationDecisionBoundary()
    adapter = RecommendationRemediationAdapter()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False

    if decision.eligible:
        planner_input = adapter.to_planner_input(
            recommendation
        )
    else:
        planner_input = None

    assert planner_input is None

def test_eligible_recommendation_reaches_existing_action_planner():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review memory usage.",
        rationale="High memory pressure requires attention.",
    )

    boundary = RemediationDecisionBoundary()
    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True

    planner_input = adapter.to_planner_input(
        recommendation
    )

    action = planner.create_action(
        planner_input
    )

    assert action is not None

def test_planned_action_remains_unauthorized_and_unexecuted():
    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review memory usage.",
        rationale="High memory pressure requires attention.",
    )

    boundary = RemediationDecisionBoundary()
    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is True

    planner_input = adapter.to_planner_input(
        recommendation
    )

    action = planner.create_action(
        planner_input
    )

    assert action is not None
    assert action.authorization_status != "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
