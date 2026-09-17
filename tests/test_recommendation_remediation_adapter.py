from engine.recommendation import Recommendation


def create_recommendation():
    return Recommendation(
        recommendation_type="REVIEW_MEMORY",
        category="MEMORY",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory pressure was detected.",
    )


def test_adapter_can_be_created():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    adapter = RecommendationRemediationAdapter()

    assert adapter is not None


def test_adapter_converts_recommendation_to_legacy_planner_format():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result == {
        "recommendation": "Review memory-intensive processes.",
        "category": "MEMORY",
        "severity": "WARNING",
    }


def test_adapter_requires_recommendation_object():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    adapter = RecommendationRemediationAdapter()

    try:
        adapter.to_planner_input({})
    except ValueError:
        return

    assert False, "Expected ValueError"


def test_adapter_preserves_description():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["recommendation"] == recommendation.description


def test_adapter_preserves_category():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["category"] == recommendation.category


def test_adapter_maps_high_priority_to_warning_severity():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["severity"] == "WARNING"

def test_adapter_maps_low_priority_to_normal_severity():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = Recommendation(
        recommendation_type="MONITOR_MEMORY",
        category="MEMORY",
        priority="LOW",
        description="Continue monitoring memory usage.",
        rationale="Memory pressure is currently low.",
    )

    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["severity"] == "NORMAL"


def test_adapter_maps_medium_priority_to_warning_severity():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = Recommendation(
        recommendation_type="INVESTIGATE_MEMORY",
        category="MEMORY",
        priority="MEDIUM",
        description="Investigate memory usage.",
        rationale="Further investigation may be useful.",
    )

    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["severity"] == "WARNING"


def test_adapter_maps_critical_priority_to_critical_severity():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = Recommendation(
        recommendation_type="ESCALATE_MEMORY",
        category="MEMORY",
        priority="CRITICAL",
        description="Escalate the memory issue.",
        rationale="The issue requires urgent attention.",
    )

    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert result["severity"] == "CRITICAL"

def test_adapter_does_not_authorize_anything():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert "authorized" not in result
    assert "authorization_status" not in result


def test_adapter_does_not_execute_anything():
    from engine.recommendation_remediation_adapter import (
        RecommendationRemediationAdapter,
    )

    recommendation = create_recommendation()
    adapter = RecommendationRemediationAdapter()

    result = adapter.to_planner_input(recommendation)

    assert "execute" not in result
    assert "executed" not in result
    assert "execution_status" not in result