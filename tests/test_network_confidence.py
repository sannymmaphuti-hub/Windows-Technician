from engine.confidence_engine import ConfidenceEngine
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


def create_confidence_engine():

    engine = ConfidenceEngine()
    engine.register_rule(
        RootCauseConfidenceRule()
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


def test_dns_root_cause_gets_medium_confidence():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1
    assert confidences[0].subject == "DNS_FAILURE"
    assert confidences[0].level == "MEDIUM"


def test_local_network_root_cause_gets_high_confidence():

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1
    assert confidences[0].subject == "LOCAL_NETWORK_FAILURE"
    assert confidences[0].level == "HIGH"


def test_network_adapter_root_cause_gets_high_confidence():

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1
    assert confidences[0].subject == "NETWORK_ADAPTER_FAILURE"
    assert confidences[0].level == "HIGH"


def test_insufficient_network_root_cause_gets_low_confidence():

    candidate = create_candidate(
        "NETWORK_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1
    assert confidences[0].subject == "NETWORK_FAILURE"
    assert confidences[0].level == "LOW"


def test_confidence_is_not_created_without_matching_evaluation():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    other_candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        other_candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert confidences == []


def test_confidence_explanation_preserves_evaluation_assessment():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    engine = create_confidence_engine()

    confidences = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(confidences) == 1
    assert "SUPPORTED" in confidences[0].explanation
    assert "MEDIUM" in confidences[0].explanation