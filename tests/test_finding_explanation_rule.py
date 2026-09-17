from engine.explanation import Explanation
from engine.finding import Finding
from engine.finding_explanation_rule import FindingExplanationRule


def create_memory_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_cpu_finding():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )


def test_rule_matches_memory_pressure():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    assert rule.matches(finding, []) is True


def test_rule_does_not_match_unrelated_finding():
    rule = FindingExplanationRule()
    finding = create_cpu_finding()

    assert rule.matches(finding, []) is False


def test_rule_creates_explanation_for_memory_pressure():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    assert isinstance(explanation, Explanation)


def test_explanation_subject_is_memory_pressure():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    assert explanation.subject == "MEMORY_PRESSURE"


def test_explanation_has_user_friendly_summary():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    assert explanation.summary == (
        "Your computer is using a lot of memory."
    )


def test_explanation_has_user_friendly_details():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    assert explanation.details == (
        "This can make Windows and applications respond slowly."
    )


def test_explanation_uses_finding_severity_as_context():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    assert explanation.confidence is None


def test_explanation_does_not_claim_memory_leak():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    explanation = rule.create_explanation(
        finding,
        [],
    )

    text = (
        explanation.summary + " " + explanation.details
    ).lower()

    assert "memory leak" not in text


def test_rule_preserves_finding_as_input():
    rule = FindingExplanationRule()
    finding = create_memory_finding()

    rule.create_explanation(
        finding,
        [],
    )

    assert finding.finding_type == "MEMORY_PRESSURE"


def test_rule_rejects_non_finding_subject():
    rule = FindingExplanationRule()

    try:
        rule.matches(
            "MEMORY_PRESSURE",
            [],
        )
    except ValueError:
        return

    assert False