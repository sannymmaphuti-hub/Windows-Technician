from engine.explanation import Explanation
from engine.explanation_engine import ExplanationEngine
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_explanation_rule import RootCauseExplanationRule


def create_engine():

    engine = ExplanationEngine()

    engine.register_rule(
        RootCauseExplanationRule()
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


def get_text(explanation):

    return (
        explanation.summary
        + " "
        + explanation.details
    ).lower()


def test_dns_failure_gets_human_explanation():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(explanations) == 1
    assert isinstance(
        explanations[0],
        Explanation,
    )

    text = get_text(explanations[0])

    assert "evidence supports" in text


def test_local_network_failure_gets_human_explanation():

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(explanations) == 1
    assert isinstance(
        explanations[0],
        Explanation,
    )

    text = get_text(explanations[0])

    assert (
        "strong evidence" in text
        or "strongly supported" in text
    )


def test_network_adapter_failure_gets_human_explanation():

    candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert len(explanations) == 1
    assert isinstance(
        explanations[0],
        Explanation,
    )

    text = get_text(explanations[0])

    assert (
        "strong evidence" in text
        or "strongly supported" in text
    )


def test_network_explanation_preserves_root_cause_identity():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert explanations[0].subject == (
        "DNS_FAILURE"
    )


def test_network_explanation_does_not_claim_certainty():

    candidate = create_candidate(
        "LOCAL_NETWORK_FAILURE"
    )

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    text = get_text(explanations[0])

    assert "definitely" not in text
    assert "guaranteed" not in text
    assert "this is certain" not in text


def test_no_network_evaluation_means_no_explanation():

    candidate = create_candidate(
        "DNS_FAILURE"
    )

    unrelated_candidate = create_candidate(
        "NETWORK_ADAPTER_FAILURE"
    )

    evaluation = create_evaluation(
        unrelated_candidate,
        "STRONGLY_SUPPORTED",
    )

    engine = create_engine()

    explanations = engine.evaluate(
        candidate,
        [evaluation],
    )

    assert explanations == []