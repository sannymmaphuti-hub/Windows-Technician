from engine.explanation import Explanation


def test_explanation_can_be_created():
    explanation = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Your computer is using a lot of memory.",
        details="This can make Windows and applications respond slowly.",
    )

    assert explanation.subject == "MEMORY_PRESSURE"
    assert explanation.summary == (
        "Your computer is using a lot of memory."
    )
    assert explanation.details == (
        "This can make Windows and applications respond slowly."
    )


def test_explanation_requires_subject():
    try:
        Explanation(
            subject="",
            summary="Memory usage is high.",
            details="Windows may become slower.",
        )
    except ValueError:
        return

    assert False


def test_explanation_requires_summary():
    try:
        Explanation(
            subject="MEMORY_PRESSURE",
            summary="",
            details="Windows may become slower.",
        )
    except ValueError:
        return

    assert False


def test_explanation_requires_details():
    try:
        Explanation(
            subject="MEMORY_PRESSURE",
            summary="Memory usage is high.",
            details="",
        )
    except ValueError:
        return

    assert False


def test_explanation_accepts_optional_confidence():
    explanation = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Your computer is using a lot of memory.",
        details="This can make Windows slower.",
        confidence="HIGH",
    )

    assert explanation.confidence == "HIGH"


def test_explanation_accepts_low_medium_and_high_confidence():
    for level in ("LOW", "MEDIUM", "HIGH"):
        explanation = Explanation(
            subject="MEMORY_PRESSURE",
            summary="Memory usage is high.",
            details="Windows may become slower.",
            confidence=level,
        )

        assert explanation.confidence == level


def test_explanation_rejects_invalid_confidence():
    try:
        Explanation(
            subject="MEMORY_PRESSURE",
            summary="Memory usage is high.",
            details="Windows may become slower.",
            confidence="CERTAIN",
        )
    except ValueError:
        return

    assert False


def test_explanation_exports_evidence():
    explanation = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Your computer is using a lot of memory.",
        details="This can make Windows slower.",
        confidence="HIGH",
    )

    evidence = explanation.to_evidence()

    assert evidence == {
        "subject": "MEMORY_PRESSURE",
        "summary": "Your computer is using a lot of memory.",
        "details": "This can make Windows slower.",
        "confidence": "HIGH",
    }


def test_explanation_does_not_claim_probability():
    explanation = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Your computer is using a lot of memory.",
        details="This can make Windows slower.",
        confidence="HIGH",
    )

    evidence = explanation.to_evidence()

    assert "probability" not in evidence
    assert "percentage" not in evidence


def test_explanation_does_not_select_root_cause():
    explanation = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Your computer is using a lot of memory.",
        details="This can make Windows slower.",
    )

    assert not hasattr(explanation, "primary_cause")
    assert not hasattr(explanation, "root_cause")

def test_explanations_with_same_values_are_equal():
    first = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Memory usage is high.",
        details="Windows may become slower.",
        confidence="HIGH",
    )

    second = Explanation(
        subject="MEMORY_PRESSURE",
        summary="Memory usage is high.",
        details="Windows may become slower.",
        confidence="HIGH",
    )

    assert first == second