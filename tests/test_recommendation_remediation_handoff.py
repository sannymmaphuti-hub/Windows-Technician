from engine.recommendation import Recommendation
from engine.remediation_action_planner import RemediationActionPlanner


def create_recommendation():
    return Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )


def test_recommendation_requires_explicit_remediation_handoff():
    recommendation = create_recommendation()

    planner = RemediationActionPlanner()

    assert recommendation is not None
    assert planner is not None


def test_recommendation_itself_has_no_remediation_action():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "remediation_action")
    assert not hasattr(recommendation, "action")


def test_recommendation_does_not_authorize_remediation_handoff():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "authorized")
    assert not hasattr(recommendation, "authorization_status")


def test_recommendation_does_not_execute_during_creation():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "executed")
    assert not hasattr(recommendation, "execution_status")


def test_remediation_planner_is_separate_from_recommendation():
    recommendation = create_recommendation()
    planner = RemediationActionPlanner()

    assert type(recommendation).__name__ == "Recommendation"
    assert type(planner).__name__ == "RemediationActionPlanner"


def test_recommendation_description_is_not_execution_instruction():
    recommendation = create_recommendation()

    assert recommendation.description == (
        "Review memory-intensive processes."
    )

    assert "execute" not in recommendation.description.lower()
    assert "run" not in recommendation.description.lower()
    assert "delete" not in recommendation.description.lower()