import pytest

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.recommendation_intelligence import RecommendationIntelligence
from engine.recommendation_remediation_adapter import RecommendationRemediationAdapter
from engine.remediation_decision_boundary import RemediationDecisionBoundary
from engine.remediation_verifier import RemediationVerifier


def test_recommendation_intelligence_ignores_unsupported_finding():
    intelligence = RecommendationIntelligence()

    finding = Finding(
        finding_type="UNKNOWN",
        description="Unsupported diagnostic condition.",
        category="UNKNOWN",
        severity="HIGH",
        supporting_signals=[],
    )

    recommendations = intelligence.generate(findings=[finding])

    assert recommendations == []


def test_recommendation_intelligence_ignores_empty_findings():
    intelligence = RecommendationIntelligence()

    recommendations = intelligence.generate(findings=[])

    assert recommendations == []


def test_recommendation_intelligence_suppresses_duplicate_recommendation_types():
    intelligence = RecommendationIntelligence()

    findings = [
        Finding(
            finding_type="MEMORY",
            description="High memory usage detected.",
            category="MEMORY",
            severity="HIGH",
            supporting_signals=[],
        ),
        Finding(
            finding_type="MEMORY",
            description="Memory pressure remains high.",
            category="MEMORY",
            severity="HIGH",
            supporting_signals=[],
        ),
    ]

    recommendations = intelligence.generate(findings=findings)

    recommendation_types = [
        recommendation.recommendation_type
        for recommendation in recommendations
    ]

    assert recommendation_types.count("memory_review") == 1


def test_decision_boundary_rejects_invalid_recommendation():
    boundary = RemediationDecisionBoundary()

    with pytest.raises(ValueError):
        boundary.evaluate("not-a-recommendation")


def test_decision_boundary_rejects_low_priority_recommendation():
    boundary = RemediationDecisionBoundary()

    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="LOW",
        description="Review memory usage.",
        rationale="Memory pressure may affect system performance.",
    )

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False


def test_decision_boundary_does_not_authorize_ineligible_recommendation():
    boundary = RemediationDecisionBoundary()

    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="MEDIUM",
        description="Review memory usage.",
        rationale="Memory pressure may affect system performance.",
    )

    decision = boundary.evaluate(recommendation)

    assert decision.eligible is False
    assert not hasattr(decision, "authorization_status")
    assert not hasattr(decision, "execution_status")


def test_adapter_rejects_invalid_recommendation():
    adapter = RecommendationRemediationAdapter()

    with pytest.raises(ValueError):
        adapter.to_planner_input("not-a-recommendation")


def test_adapter_preserves_recommendation_information():
    adapter = RecommendationRemediationAdapter()

    recommendation = Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review memory usage.",
        rationale="High memory pressure was detected.",
    )

    planner_input = adapter.to_planner_input(recommendation)

    assert planner_input["recommendation"] == recommendation.description
    assert planner_input["category"] == recommendation.category
    assert planner_input["severity"] == "WARNING"


def test_verification_detects_contradictory_observed_state():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_pressure": "NORMAL"},
        observed={"memory_pressure": "HIGH"},
        action_id="negative-action-1",
    )

    assert result["verified"] is False
    assert result["action_id"] == "negative-action-1"


def test_verification_does_not_mutate_expected_or_observed_evidence():
    verifier = RemediationVerifier()

    expected = {"status": "resolved"}
    observed = {"status": "unresolved"}

    verifier.verify(
        expected=expected,
        observed=observed,
        action_id="negative-action-2",
    )

    assert expected == {"status": "resolved"}
    assert observed == {"status": "unresolved"}


def test_verification_preserves_failed_verification_boundary():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"service": "running"},
        observed={"service": "stopped"},
        action_id="negative-action-3",
    )

    assert result["verified"] is False
    assert result["action_id"] == "negative-action-3"