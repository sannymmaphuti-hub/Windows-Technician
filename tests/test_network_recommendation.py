from engine.recommendation import Recommendation
from engine.recommendation_engine import RecommendationEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_recommendation_rule import RootCauseRecommendationRule


def create_engine():

    engine = RecommendationEngine()

    engine.register_rule(
        RootCauseRecommendationRule()
    )

    return engine


def create_candidate(cause_type):

    return RootCauseCandidate(
        cause_type=cause_type,
        category="NETWORK",
        explanation="Network root cause candidate.",
    )


def create_evaluation(
    candidate,
    assessment,
):

    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Network root cause evaluation.",
    )


def test_root_cause_recommendation_rule_requires_evaluation():

    rule = RootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    assert rule.matches(
        candidate,
        [],
    ) is False


def test_root_cause_recommendation_rule_accepts_supported_network_cause():

    rule = RootCauseRecommendationRule()

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_root_cause_recommendation_rule_accepts_strong_network_cause():

    rule = RootCauseRecommendationRule()

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True