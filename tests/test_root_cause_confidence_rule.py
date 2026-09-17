import pytest

from engine.confidence import Confidence
from engine.confidence_rule import ConfidenceRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_confidence_rule import RootCauseConfidenceRule
from engine.root_cause_evaluation import RootCauseEvaluation


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation="A memory-intensive process may be contributing.",
    )


def create_evaluation(assessment):
    candidate = create_candidate()

    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Evaluation result.",
    )


def test_root_cause_confidence_rule_is_a_confidence_rule():
    rule = RootCauseConfidenceRule()

    assert isinstance(rule, ConfidenceRule)


def test_rule_matches_insufficient_evaluation():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("INSUFFICIENT")

    assert rule.matches(evaluation.candidate, [evaluation]) is True


def test_rule_matches_supported_evaluation():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("SUPPORTED")

    assert rule.matches(evaluation.candidate, [evaluation]) is True


def test_rule_matches_strongly_supported_evaluation():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("STRONGLY_SUPPORTED")

    assert rule.matches(evaluation.candidate, [evaluation]) is True


def test_rule_does_not_match_unrelated_subject():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("SUPPORTED")

    unrelated_candidate = RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation="A memory leak may be contributing.",
    )

    assert rule.matches(
        unrelated_candidate,
        [evaluation],
    ) is False


def test_insufficient_evidence_produces_low_confidence():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("INSUFFICIENT")

    confidence = rule.create_confidence(
        evaluation.candidate,
        [evaluation],
    )

    assert isinstance(confidence, Confidence)
    assert confidence.level == "LOW"


def test_supported_evidence_produces_medium_confidence():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("SUPPORTED")

    confidence = rule.create_confidence(
        evaluation.candidate,
        [evaluation],
    )

    assert isinstance(confidence, Confidence)
    assert confidence.level == "MEDIUM"


def test_strongly_supported_evidence_produces_high_confidence():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("STRONGLY_SUPPORTED")

    confidence = rule.create_confidence(
        evaluation.candidate,
        [evaluation],
    )

    assert isinstance(confidence, Confidence)
    assert confidence.level == "HIGH"


def test_confidence_subject_is_candidate():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("SUPPORTED")

    confidence = rule.create_confidence(
        evaluation.candidate,
        [evaluation],
    )

    assert confidence.subject == "MEMORY_INTENSIVE_PROCESS"


def test_confidence_does_not_claim_probability():
    rule = RootCauseConfidenceRule()

    evaluation = create_evaluation("STRONGLY_SUPPORTED")

    confidence = rule.create_confidence(
        evaluation.candidate,
        [evaluation],
    )

    assert not hasattr(confidence, "probability")