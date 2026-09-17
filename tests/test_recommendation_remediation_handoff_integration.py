from engine.recommendation import Recommendation
from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action_planner import RemediationActionPlanner


def create_recommendation():
    return Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )


def test_recommendation_can_be_handed_to_remediation_planner():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action is not None


def test_handoff_preserves_recommendation_description():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.description == recommendation.description


def test_handoff_preserves_category():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.category == recommendation.category


def test_handoff_maps_priority_to_action_severity():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.severity == "WARNING"


def test_handoff_action_starts_unauthorized():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.authorization_status == "UNAUTHORIZED"


def test_handoff_action_starts_unexecuted():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.execution_status == "NOT_EXECUTED"


def test_handoff_does_not_assign_operation():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.operation is None


def test_handoff_does_not_execute_action():
    recommendation = create_recommendation()

    adapter = RecommendationRemediationAdapter()
    planner = RemediationActionPlanner()

    planner_input = adapter.to_planner_input(recommendation)
    action = planner.create_action(planner_input)

    assert action.execution_status == "NOT_EXECUTED"