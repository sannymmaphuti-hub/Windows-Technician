from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_explanation_rule import RootCauseExplanationRule


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the memory pressure."
        ),
    )


def create_evaluation(candidate, assessment):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Root cause evaluation result.",
    )


def test_rule_can_be_created():
    rule = RootCauseExplanationRule()

    assert isinstance(rule, ExplanationRule)


def test_rule_matches_root_cause_candidate():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(candidate, "SUPPORTED")

    assert rule.matches(
        candidate,
        [evaluation],
    ) is True


def test_rule_rejects_unrelated_subject():
    rule = RootCauseExplanationRule()

    candidate = create_candidate()
    unrelated_candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A possible memory leak.",
    )

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    assert rule.matches(
        unrelated_candidate,
        [evaluation],
    ) is False


def test_rule_requires_root_cause_candidate():
    rule = RootCauseExplanationRule()
    evaluation = create_evaluation(
        create_candidate(),
        "SUPPORTED",
    )

    try:
        rule.matches(
            "MEMORY_INTENSIVE_PROCESS",
            [evaluation],
        )
    except ValueError:
        return

    assert False


def test_insufficient_evidence_is_explained_as_uncertain():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    explanation = rule.create_explanation(
        candidate,
        [evaluation],
    )

    assert isinstance(explanation, Explanation)
    assert explanation.subject == "MEMORY_INTENSIVE_PROCESS"

    text = (
        explanation.summary + " " + explanation.details
    ).lower()

    assert "possible" in text
    assert (
        "not enough evidence" in text
        or "insufficient evidence" in text
    )


def test_supported_root_cause_is_explained_as_supported():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    explanation = rule.create_explanation(
        candidate,
        [evaluation],
    )

    text = (
        explanation.summary + " " + explanation.details
    ).lower()

    assert "evidence supports" in text


def test_strongly_supported_root_cause_uses_stronger_language():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    explanation = rule.create_explanation(
        candidate,
        [evaluation],
    )

    text = (
        explanation.summary + " " + explanation.details
    ).lower()

    assert (
        "strongly supported" in text
        or "strong evidence" in text
    )


def test_root_cause_explanation_does_not_claim_absolute_certainty():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    explanation = rule.create_explanation(
        candidate,
        [evaluation],
    )

    text = (
        explanation.summary + " " + explanation.details
    ).lower()

    assert "definitely" not in text
    assert "guaranteed" not in text
    assert "this is certain" not in text
    assert "this is definitely the cause" not in text
    assert "the cause is certain" not in text


def test_root_cause_explanation_does_not_claim_probability():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    explanation = rule.create_explanation(
        candidate,
        [evaluation],
    )

    evidence = explanation.to_evidence()

    assert "probability" not in evidence
    assert "percentage" not in evidence


def test_root_cause_explanation_does_not_mutate_evaluation():
    rule = RootCauseExplanationRule()
    candidate = create_candidate()
    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    original_assessment = evaluation.assessment

    rule.create_explanation(
        candidate,
        [evaluation],
    )

    assert evaluation.assessment == original_assessment