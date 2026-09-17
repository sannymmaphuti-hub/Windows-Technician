from engine.recommendation import Recommendation


def create_recommendation():
    return Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )


def test_recommendation_contains_information_needed_for_handoff():
    recommendation = create_recommendation()

    assert recommendation.recommendation_type == "REVIEW_MEMORY"
    assert recommendation.category == "MEMORY"
    assert recommendation.priority == "HIGH"
    assert recommendation.description
    assert recommendation.rationale


def test_recommendation_handoff_information_is_descriptive():
    recommendation = create_recommendation()

    exported = recommendation.to_evidence()

    assert exported["recommendation_type"] == "REVIEW_MEMORY"
    assert exported["category"] == "MEMORY"
    assert exported["priority"] == "HIGH"
    assert exported["description"] == (
        "Review memory-intensive processes."
    )


def test_recommendation_does_not_decide_execution():
    recommendation = create_recommendation()

    exported = recommendation.to_evidence()

    assert "execute" not in exported
    assert "executed" not in exported
    assert "execution_status" not in exported


def test_recommendation_does_not_decide_authorization():
    recommendation = create_recommendation()

    exported = recommendation.to_evidence()

    assert "authorized" not in exported
    assert "authorization_status" not in exported


def test_recommendation_priority_is_not_remediation_authorization():
    recommendation = create_recommendation()

    assert recommendation.priority == "HIGH"

    assert not hasattr(
        recommendation,
        "authorization_status",
    )


def test_recommendation_handoff_must_preserve_category():
    recommendation = create_recommendation()

    assert recommendation.category == "MEMORY"


def test_recommendation_handoff_must_preserve_description():
    recommendation = create_recommendation()

    assert recommendation.description == (
        "Review memory-intensive processes."
    )


def test_recommendation_handoff_must_not_execute_anything():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "execute")