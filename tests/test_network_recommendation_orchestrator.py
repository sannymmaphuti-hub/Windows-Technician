from engine.network_recommendation_orchestrator import (
    NetworkRecommendationOrchestrator,
)
from engine.network_root_cause_recommendation_rule import (
    NetworkRootCauseRecommendationRule,
)
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


def create_candidate(cause_type):
    return RootCauseCandidate(
        cause_type=cause_type,
        category="NETWORK",
        explanation="Network root cause candidate.",
    )


def create_evaluation(candidate, assessment):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Network root cause evaluation.",
    )


def create_orchestrator():
    return NetworkRecommendationOrchestrator(
        recommendation_rule=NetworkRootCauseRecommendationRule()
    )


def test_dns_failure_produces_dns_recommendation():

    candidate = create_candidate("DNS_FAILURE")

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == (
        "REVIEW_DNS_CONFIGURATION"
    )
    assert recommendations[0].category == "NETWORK"
    assert recommendations[0].priority == "MEDIUM"


def test_local_network_failure_produces_local_network_recommendation():

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == (
        "REVIEW_LOCAL_NETWORK"
    )
    assert recommendations[0].category == "NETWORK"
    assert recommendations[0].priority == "HIGH"


def test_network_adapter_failure_produces_adapter_recommendation():

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert len(recommendations) == 1
    assert recommendations[0].recommendation_type == (
        "REVIEW_NETWORK_ADAPTER"
    )
    assert recommendations[0].category == "NETWORK"
    assert recommendations[0].priority == "HIGH"


def test_missing_evaluation_produces_no_recommendation():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [],
    )

    assert recommendations == []


def test_insufficient_evaluation_produces_no_recommendation():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert recommendations == []


def test_unsupported_root_cause_produces_no_recommendation():

    candidate = create_candidate(
        "UNKNOWN_NETWORK_CAUSE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert recommendations == []

def test_no_primary_cause_produces_no_recommendation():

    recommendations = create_orchestrator().recommend(
        None,
        [],
    )

    assert recommendations == []


def test_recommendation_does_not_mutate_candidate_or_evaluations():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    original_cause_type = candidate.cause_type
    original_assessment = evaluation.assessment
    original_evidence = list(
        evaluation.supporting_evidence
    )

    recommendations = create_orchestrator().recommend(
        candidate,
        [evaluation],
    )

    assert len(recommendations) == 1
    assert candidate.cause_type == original_cause_type
    assert evaluation.assessment == original_assessment
    assert (
        evaluation.supporting_evidence
        == original_evidence
    )