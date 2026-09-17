import pytest

from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


def create_candidate(cause_type):
    return RootCauseCandidate(
        cause_type=cause_type,
        category="MEMORY",
        explanation=(
            f"{cause_type} may be contributing "
            "to the memory pressure."
        ),
    )


def create_confidence(candidate, level):
    return Confidence(
        subject=candidate.cause_type,
        level=level,
        explanation=(
            f"Confidence is {level} for this root cause."
        ),
    )


def create_evidence(candidates, confidences):
    return {
        "candidates": candidates,
        "confidences": confidences,
        "primary_cause": None,
    }


def test_competing_rule_can_be_created():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    rule = CompetingRootCauseExplanationRule()

    assert isinstance(rule, ExplanationRule)


def test_rule_requires_candidate_list():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    rule = CompetingRootCauseExplanationRule()

    with pytest.raises(ValueError):
        rule.matches(
            "not a candidate list",
            {},
        )


def test_rule_matches_multiple_candidates_without_primary():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    evidence = create_evidence(
        [candidate_a, candidate_b],
        [],
    )

    rule = CompetingRootCauseExplanationRule()

    assert rule.matches(
        evidence["candidates"],
        evidence,
    )


def test_rule_does_not_match_single_candidate():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )

    evidence = create_evidence(
        [candidate],
        [],
    )

    rule = CompetingRootCauseExplanationRule()

    assert not rule.matches(
        evidence["candidates"],
        evidence,
    )


def test_rule_does_not_match_when_primary_cause_exists():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    evidence = create_evidence(
        [candidate_a, candidate_b],
        [],
    )

    evidence["primary_cause"] = candidate_a

    rule = CompetingRootCauseExplanationRule()

    assert not rule.matches(
        evidence["candidates"],
        evidence,
    )


def test_competing_causes_are_explained_as_uncertain():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    evidence = create_evidence(
        [candidate_a, candidate_b],
        [],
    )

    rule = CompetingRootCauseExplanationRule()

    explanation = rule.create_explanation(
        evidence["candidates"],
        evidence,
    )

    assert isinstance(explanation, Explanation)

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "several possible causes" in text
    assert "single primary cause" in text


def test_competing_causes_do_not_claim_one_is_the_cause():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    evidence = create_evidence(
        [candidate_a, candidate_b],
        [],
    )

    rule = CompetingRootCauseExplanationRule()

    explanation = rule.create_explanation(
        evidence["candidates"],
        evidence,
    )

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "the cause is" not in text
    assert "this is the cause" not in text
    assert "definitely" not in text
    assert "guaranteed" not in text


def test_competing_causes_can_include_confidence_information():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    confidence_a = create_confidence(
        candidate_a,
        "MEDIUM",
    )
    confidence_b = create_confidence(
        candidate_b,
        "MEDIUM",
    )

    evidence = create_evidence(
        [candidate_a, candidate_b],
        [confidence_a, confidence_b],
    )

    rule = CompetingRootCauseExplanationRule()

    explanation = rule.create_explanation(
        evidence["candidates"],
        evidence,
    )

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "evidence" in text
    assert explanation.confidence == "MEDIUM"


def test_competing_rule_does_not_mutate_candidates():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    candidate_a = create_candidate(
        "MEMORY_INTENSIVE_PROCESS"
    )
    candidate_b = create_candidate(
        "MEMORY_LEAK"
    )

    candidates = [candidate_a, candidate_b]

    original = list(candidates)

    evidence = create_evidence(
        candidates,
        [],
    )

    rule = CompetingRootCauseExplanationRule()

    rule.create_explanation(
        candidates,
        evidence,
    )

    assert candidates == original


def test_competing_rule_requires_at_least_two_candidates():
    from engine.competing_root_cause_explanation_rule import (
        CompetingRootCauseExplanationRule,
    )

    rule = CompetingRootCauseExplanationRule()

    with pytest.raises(ValueError):
        rule.create_explanation(
            [],
            {
                "candidates": [],
                "confidences": [],
                "primary_cause": None,
            },
        )