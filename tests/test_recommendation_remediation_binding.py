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

def test_recommendation_is_not_bound_automatically():
    recommendation = create_recommendation()
    assert not hasattr(recommendation, "operation")
    assert not hasattr(recommendation, "operation_id")
    assert not hasattr(recommendation, "remediation_action")

def test_recommendation_is_separate_from_remediation():
    recommendation = create_recommendation()
    assert type(recommendation).__name__ == "Recommendation"


def test_recommendation_does_not_authorize_binding():
    recommendation = create_recommendation()
    assert not hasattr(recommendation, "authorized")
    assert not hasattr(recommendation, "is_authorized")


def test_recommendation_creation_does_not_execute_operation():
    recommendation = create_recommendation()
    assert not hasattr(recommendation, "executed")
    assert not hasattr(recommendation, "is_executed")

def test_recommendation_can_exist_without_binding():
    recommendation = create_recommendation()
    assert recommendation.recommendation_type == "REVIEW_MEMORY"
    assert recommendation.category == "MEMORY"


def test_recommendation_does_not_contain_operation_mapping():
    recommendation = create_recommendation()
    exported = recommendation.to_evidence()
    assert "operation" not in exported
    assert "operation_id" not in exported
    assert "remediation" not in exported

def test_recommendation_does_not_contain_execution_permission():
    recommendation = create_recommendation()
    exported = recommendation.to_evidence()
    assert "authorized" not in exported
    assert "authorization" not in exported
    assert "permission" not in exported
