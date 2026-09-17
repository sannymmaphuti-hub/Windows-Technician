import pytest

from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


def create_candidate():
    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the memory pressure."
        ),
    )


def test_audience_rule_can_be_created():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    rule = AudienceExplanationRule()

    assert isinstance(rule, ExplanationRule)


def test_user_audience_is_supported():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    rule = AudienceExplanationRule()

    assert rule.is_supported_audience("USER")


def test_technician_audience_is_supported():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    rule = AudienceExplanationRule()

    assert rule.is_supported_audience("TECHNICIAN")


def test_unknown_audience_is_rejected():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    rule = AudienceExplanationRule()

    assert not rule.is_supported_audience("UNKNOWN")


def test_user_explanation_uses_plain_language():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    candidate = create_candidate()

    rule = AudienceExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [],
        "USER",
    )

    assert isinstance(explanation, Explanation)

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "computer" in text
    assert "memory" in text


def test_technician_explanation_contains_technical_context():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    candidate = create_candidate()

    rule = AudienceExplanationRule()

    explanation = rule.create_explanation(
        candidate,
        [],
        "TECHNICIAN",
    )

    assert isinstance(explanation, Explanation)

    text = (
        explanation.summary.lower()
        + " "
        + explanation.details.lower()
    )

    assert "memory-intensive process" in text
    assert "evidence" in text


def test_user_and_technician_explanations_are_different():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    candidate = create_candidate()

    rule = AudienceExplanationRule()

    user_explanation = rule.create_explanation(
        candidate,
        [],
        "USER",
    )

    technician_explanation = rule.create_explanation(
        candidate,
        [],
        "TECHNICIAN",
    )

    assert (
        user_explanation.summary
        != technician_explanation.summary
    )

    assert (
        user_explanation.details
        != technician_explanation.details
    )


def test_both_audiences_refer_to_same_subject():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    candidate = create_candidate()

    rule = AudienceExplanationRule()

    user_explanation = rule.create_explanation(
        candidate,
        [],
        "USER",
    )

    technician_explanation = rule.create_explanation(
        candidate,
        [],
        "TECHNICIAN",
    )

    assert user_explanation.subject == candidate.cause_type
    assert (
        technician_explanation.subject
        == candidate.cause_type
    )


def test_unknown_audience_is_rejected_when_creating_explanation():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    candidate = create_candidate()

    rule = AudienceExplanationRule()

    with pytest.raises(ValueError):
        rule.create_explanation(
            candidate,
            [],
            "UNKNOWN",
        )


def test_invalid_subject_is_rejected():
    from engine.audience_explanation_rule import (
        AudienceExplanationRule,
    )

    rule = AudienceExplanationRule()

    with pytest.raises(ValueError):
        rule.create_explanation(
            "not a candidate",
            [],
            "USER",
        )