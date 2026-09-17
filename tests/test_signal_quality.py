import pytest

from engine.signal import Signal


def test_signal_can_have_quality():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        quality="HIGH",
    )

    assert signal.quality == "HIGH"


def test_signal_accepts_medium_quality():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        quality="MEDIUM",
    )

    assert signal.quality == "MEDIUM"


def test_signal_accepts_low_quality():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        quality="LOW",
    )

    assert signal.quality == "LOW"


def test_signal_rejects_invalid_quality():
    with pytest.raises(ValueError):
        Signal(
            signal_type="HIGH_MEMORY_USAGE",
            source="memory",
            subject="system_memory",
            attribute="usage_percent",
            value=97,
            quality="INVALID",
        )


def test_signal_can_have_no_quality_for_backward_compatibility():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
    )

    assert signal.quality is None


def test_signal_quality_is_exported_as_evidence():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        quality="HIGH",
    )

    evidence = signal.to_evidence()

    assert evidence["quality"] == "HIGH"


def test_signal_quality_does_not_change_signal_identity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        quality="HIGH",
    )

    assert signal.signal_type == "HIGH_MEMORY_USAGE"
    assert signal.source == "memory"
    assert signal.subject == "system_memory"
    assert signal.attribute == "usage_percent"
    assert signal.value == 97