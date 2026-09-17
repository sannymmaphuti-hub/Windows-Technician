from engine.explanation_rule import ExplanationRule


class FakeExplanationRule(ExplanationRule):

    def matches(self, subject, evidence):
        return subject == "MEMORY_PRESSURE"

    def create_explanation(self, subject, evidence):
        return {
            "subject": subject,
            "evidence": evidence,
        }


def test_explanation_rule_can_be_subclassed():
    rule = FakeExplanationRule()

    assert isinstance(rule, ExplanationRule)


def test_explanation_rule_matches_can_be_called():
    rule = FakeExplanationRule()

    assert rule.matches(
        "MEMORY_PRESSURE",
        [],
    )


def test_explanation_rule_matches_can_reject():
    rule = FakeExplanationRule()

    assert not rule.matches(
        "CPU_PRESSURE",
        [],
    )


def test_explanation_rule_can_create_explanation():
    rule = FakeExplanationRule()

    explanation = rule.create_explanation(
        "MEMORY_PRESSURE",
        [],
    )

    assert explanation["subject"] == "MEMORY_PRESSURE"


def test_explanation_rule_requires_matches():
    class InvalidRule(ExplanationRule):

        def create_explanation(self, subject, evidence):
            return None

    try:
        InvalidRule()
    except TypeError:
        return

    assert False


def test_explanation_rule_requires_create_explanation():
    class InvalidRule(ExplanationRule):

        def matches(self, subject, evidence):
            return True

    try:
        InvalidRule()
    except TypeError:
        return

    assert False


def test_explanation_rule_is_not_directly_instantiable():
    try:
        ExplanationRule()
    except TypeError:
        return

    assert False


def test_explanation_rule_preserves_evidence():
    rule = FakeExplanationRule()

    evidence = ["MEMORY_PRESSURE"]

    result = rule.create_explanation(
        "MEMORY_PRESSURE",
        evidence,
    )

    assert result["evidence"] is evidence