import pytest

from engine.recommendation import Recommendation


def create_recommendation():
    return Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )


def test_recommendation_is_not_a_remediation_action():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "execute")
    assert not hasattr(recommendation, "run")


def test_recommendation_does_not_contain_authorization_state():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "authorized")
    assert not hasattr(recommendation, "is_authorized")


def test_recommendation_does_not_contain_execution_state():
    recommendation = create_recommendation()

    assert not hasattr(recommendation, "executed")
    assert not hasattr(recommendation, "is_executed")


def test_recommendation_can_exist_without_remediation_binding():
    recommendation = create_recommendation()

    assert recommendation is not None
    assert recommendation.recommendation_type == "REVIEW_MEMORY"


def test_recommendation_does_not_create_remediation_implicitly():
    recommendation = create_recommendation()

    exported = recommendation.to_evidence()

    assert "remediation" not in exported
    assert "action" not in exported


def test_recommendation_does_not_grant_authority():
    recommendation = create_recommendation()

    exported = recommendation.to_evidence()

    assert "authorized" not in exported
    assert "authorization" not in exported


def test_recommendation_is_descriptive_not_executive():
    recommendation = create_recommendation()

    assert recommendation.description
    assert recommendation.rationale

    assert not callable(
        getattr(recommendation, "execute", None)
    )