import pytest

from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.network_root_cause_recommendation_rule import (
    NetworkRootCauseRecommendationRule,
)


def create_candidate(cause_type, explanation):
    return RootCauseCandidate(
        cause_type=cause_type,
        category="NETWORK",
        explanation=explanation,
    )


def create_evaluation(candidate, assessment="SUPPORTED"):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Evidence supports the possible network cause.",
    )


def test_network_rule_is_recommendation_rule():
    rule = NetworkRootCauseRecommendationRule()

    assert isinstance(rule, RecommendationRule)


def test_rule_matches_supported_dns_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    evaluation = create_evaluation(candidate, "SUPPORTED")

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_matches_strongly_supported_dns_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_matches_supported_local_network_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE",
        "The local network gateway may be unreachable.",
    )

    evaluation = create_evaluation(candidate, "SUPPORTED")

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_matches_strongly_supported_local_network_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE",
        "The local network gateway may be unreachable.",
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_matches_supported_network_adapter_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE",
        "The network adapter is disconnected.",
    )

    evaluation = create_evaluation(candidate, "SUPPORTED")

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_matches_strongly_supported_network_adapter_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE",
        "The network adapter is disconnected.",
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_does_not_match_insufficient_dns_failure():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution may be failing.",
    )

    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is False


def test_rule_does_not_match_unrelated_candidate():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "UPSTREAM_INTERNET_FAILURE",
        "An upstream Internet problem may exist.",
    )

    other_candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    evaluation = create_evaluation(
        other_candidate,
        "SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is False


def test_dns_failure_creates_dns_recommendation():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    recommendation = rule.create_recommendation(
        candidate,
        [evaluation],
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_DNS_CONFIGURATION"
    )
    assert recommendation.category == "NETWORK"
    assert recommendation.priority == "MEDIUM"
    assert "DNS" in recommendation.description


def test_local_network_failure_creates_gateway_recommendation():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE",
        "The local network gateway may be unreachable.",
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    recommendation = rule.create_recommendation(
        candidate,
        [evaluation],
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_LOCAL_NETWORK"
    )
    assert recommendation.category == "NETWORK"
    assert recommendation.priority == "HIGH"
    assert "network" in recommendation.description.lower()


def test_network_adapter_failure_creates_adapter_recommendation():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE",
        "The network adapter is disconnected.",
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    recommendation = rule.create_recommendation(
        candidate,
        [evaluation],
    )

    assert isinstance(recommendation, Recommendation)
    assert recommendation.recommendation_type == (
        "REVIEW_NETWORK_ADAPTER"
    )
    assert recommendation.category == "NETWORK"
    assert recommendation.priority == "HIGH"
    assert "adapter" in recommendation.description.lower()


def test_supported_network_causes_have_medium_priority():
    rule = NetworkRootCauseRecommendationRule()

    candidates = [
        create_candidate(
            "DNS_FAILURE",
            "DNS resolution is failing.",
        ),
        create_candidate(
            "LOCAL_NETWORK_FAILURE",
            "The local network gateway may be unreachable.",
        ),
        create_candidate(
            "NETWORK_ADAPTER_FAILURE",
            "The network adapter is disconnected.",
        ),
    ]

    for candidate in candidates:
        recommendation = rule.create_recommendation(
            candidate,
            [create_evaluation(candidate, "SUPPORTED")],
        )

        assert recommendation.priority == "MEDIUM"


def test_strongly_supported_network_causes_have_high_priority():
    rule = NetworkRootCauseRecommendationRule()

    candidates = [
        create_candidate(
            "DNS_FAILURE",
            "DNS resolution is failing.",
        ),
        create_candidate(
            "LOCAL_NETWORK_FAILURE",
            "The local network gateway may be unreachable.",
        ),
        create_candidate(
            "NETWORK_ADAPTER_FAILURE",
            "The network adapter is disconnected.",
        ),
    ]

    for candidate in candidates:
        recommendation = rule.create_recommendation(
            candidate,
            [create_evaluation(candidate, "STRONGLY_SUPPORTED")],
        )

        assert recommendation.priority == "HIGH"


def test_rule_rejects_invalid_candidate():
    rule = NetworkRootCauseRecommendationRule()

    with pytest.raises(ValueError):
        rule.matches(None, [])


def test_rule_rejects_invalid_evidence():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    with pytest.raises(ValueError):
        rule.matches(candidate, None)


def test_rule_rejects_missing_evaluation():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE",
        "DNS resolution is failing.",
    )

    with pytest.raises(ValueError):
        rule.create_recommendation(candidate, [])


def test_rule_does_not_create_recommendation_for_unsupported_cause():
    rule = NetworkRootCauseRecommendationRule()

    candidate = create_candidate(
        "UPSTREAM_INTERNET_FAILURE",
        "An upstream Internet problem may exist.",
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    with pytest.raises(ValueError):
        rule.create_recommendation(
            candidate,
            [evaluation],
        )