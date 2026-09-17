import pytest

from engine.recommendation import Recommendation


def test_recommendation_can_be_created():
    recommendation = Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )

    assert recommendation.recommendation_type == "REVIEW_MEMORY"
    assert recommendation.category == "MEMORY"
    assert recommendation.priority == "MEDIUM"
    assert recommendation.description == (
        "Review memory-intensive processes."
    )
    assert recommendation.rationale == (
        "High memory pressure was detected."
    )


def test_recommendation_exports_to_evidence():
    recommendation = Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )

    assert recommendation.to_evidence() == {
        "recommendation_type": "REVIEW_MEMORY",
        "category": "MEMORY",
        "priority": "MEDIUM",
        "description": "Review memory-intensive processes.",
        "rationale": "High memory pressure was detected.",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("recommendation_type", ""),
        ("category", ""),
        ("description", ""),
        ("rationale", ""),
    ],
)
def test_recommendation_rejects_empty_text(field, value):
    values = {
        "recommendation_type": "REVIEW_MEMORY",
        "category": "MEMORY",
        "priority": "MEDIUM",
        "description": "Review memory-intensive processes.",
        "rationale": "High memory pressure was detected.",
    }

    values[field] = value

    with pytest.raises(ValueError):
        Recommendation(**values)


@pytest.mark.parametrize(
    "field,value",
    [
        ("recommendation_type", 123),
        ("category", 123),
        ("description", 123),
        ("rationale", 123),
    ],
)
def test_recommendation_rejects_non_string_text(field, value):
    values = {
        "recommendation_type": "REVIEW_MEMORY",
        "category": "MEMORY",
        "priority": "MEDIUM",
        "description": "Review memory-intensive processes.",
        "rationale": "High memory pressure was detected.",
    }

    values[field] = value

    with pytest.raises(ValueError):
        Recommendation(**values)


@pytest.mark.parametrize(
    "priority",
    ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
)
def test_recommendation_accepts_valid_priority(priority):
    recommendation = Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority=priority,
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )

    assert recommendation.priority == priority


def test_recommendation_rejects_invalid_priority():
    with pytest.raises(ValueError):
        Recommendation(
            recommendation_type="REVIEW_MEMORY",
            category="MEMORY",
            priority="INVALID",
            description="Review memory-intensive processes.",
            rationale="High memory pressure was detected.",
        )