import pytest

from engine.finding import Finding


def test_finding_can_be_created():
    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )

    assert finding.finding_type == "MEMORY_PRESSURE"
    assert finding.category == "MEMORY"
    assert finding.severity == "HIGH"
    assert finding.description == "System memory pressure is high."


def test_finding_requires_valid_finding_type():
    with pytest.raises(ValueError):
        Finding(
            finding_type="",
            category="MEMORY",
            severity="HIGH",
            description="System memory pressure is high.",
        )


def test_finding_requires_valid_category():
    with pytest.raises(ValueError):
        Finding(
            finding_type="MEMORY_PRESSURE",
            category="",
            severity="HIGH",
            description="System memory pressure is high.",
        )


def test_finding_requires_valid_severity():
    with pytest.raises(ValueError):
        Finding(
            finding_type="MEMORY_PRESSURE",
            category="MEMORY",
            severity="UNKNOWN",
            description="System memory pressure is high.",
        )


def test_finding_requires_valid_description():
    with pytest.raises(ValueError):
        Finding(
            finding_type="MEMORY_PRESSURE",
            category="MEMORY",
            severity="HIGH",
            description="",
        )


def test_finding_accepts_supporting_signals():
    supporting_signals = ["signal-one", "signal-two"]

    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=supporting_signals,
    )

    assert finding.supporting_signals == supporting_signals


def test_finding_can_have_no_supporting_signals():
    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )

    assert finding.supporting_signals == []


def test_finding_exports_its_information():
    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )

    evidence = finding.to_evidence()

    assert evidence == {
        "finding_type": "MEMORY_PRESSURE",
        "category": "MEMORY",
        "severity": "HIGH",
        "description": "System memory pressure is high.",
        "supporting_signals": [],
    }


def test_finding_severity_is_independent_from_signal_strength():
    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="LOW",
        description="System memory pressure is present.",
    )

    assert finding.severity == "LOW"