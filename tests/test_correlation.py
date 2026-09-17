import pytest

from engine.correlation import Correlation
from engine.finding import Finding


def create_finding(finding_type="MEMORY_PRESSURE"):
    return Finding(
        finding_type=finding_type,
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def test_correlation_can_be_created():
    finding = create_finding()

    correlation = Correlation(
        correlation_type="RESOURCE_CONTENTION",
        findings=[finding],
        strength="MEDIUM",
        explanation="The findings may be related.",
    )

    assert correlation.correlation_type == "RESOURCE_CONTENTION"
    assert correlation.findings == [finding]
    assert correlation.strength == "MEDIUM"
    assert correlation.explanation == "The findings may be related."


def test_correlation_requires_correlation_type():
    with pytest.raises(ValueError):
        Correlation(
            correlation_type="",
            findings=[create_finding()],
            strength="MEDIUM",
            explanation="The findings may be related.",
        )


def test_correlation_requires_findings():
    with pytest.raises(ValueError):
        Correlation(
            correlation_type="RESOURCE_CONTENTION",
            findings=[],
            strength="MEDIUM",
            explanation="The findings may be related.",
        )


def test_correlation_requires_valid_strength():
    with pytest.raises(ValueError):
        Correlation(
            correlation_type="RESOURCE_CONTENTION",
            findings=[create_finding()],
            strength="INVALID",
            explanation="The findings may be related.",
        )


def test_correlation_requires_explanation():
    with pytest.raises(ValueError):
        Correlation(
            correlation_type="RESOURCE_CONTENTION",
            findings=[create_finding()],
            strength="MEDIUM",
            explanation="",
        )


def test_correlation_preserves_finding_objects():
    finding = create_finding()

    correlation = Correlation(
        correlation_type="RESOURCE_CONTENTION",
        findings=[finding],
        strength="HIGH",
        explanation="The findings may be related.",
    )

    assert correlation.findings[0] is finding


def test_correlation_exports_evidence():
    finding = create_finding()

    correlation = Correlation(
        correlation_type="RESOURCE_CONTENTION",
        findings=[finding],
        strength="MEDIUM",
        explanation="The findings may be related.",
    )

    evidence = correlation.to_evidence()

    assert evidence["correlation_type"] == "RESOURCE_CONTENTION"
    assert evidence["findings"] == [finding]
    assert evidence["strength"] == "MEDIUM"
    assert evidence["explanation"] == "The findings may be related."


def test_correlation_strength_is_independent_of_finding_severity():
    finding = create_finding()

    correlation = Correlation(
        correlation_type="RESOURCE_CONTENTION",
        findings=[finding],
        strength="LOW",
        explanation="The findings may be related.",
    )

    assert finding.severity == "HIGH"
    assert correlation.strength == "LOW"