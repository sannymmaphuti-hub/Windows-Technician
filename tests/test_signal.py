import pytest

from engine.signal import Signal


def test_signal_can_represent_a_diagnostic_signal():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    assert signal.signal_type == "HIGH_MEMORY_USAGE"
    assert signal.source == "memory"
    assert signal.subject == "system_memory"
    assert signal.attribute == "usage_percent"
    assert signal.value == 88


def test_signal_requires_signal_type():
    with pytest.raises(ValueError):
        Signal(
            signal_type="",
            source="memory",
            subject="system_memory",
            attribute="usage_percent",
            value=88,
        )


def test_signal_requires_source():
    with pytest.raises(ValueError):
        Signal(
            signal_type="HIGH_MEMORY_USAGE",
            source="",
            subject="system_memory",
            attribute="usage_percent",
            value=88,
        )


def test_signal_requires_subject():
    with pytest.raises(ValueError):
        Signal(
            signal_type="HIGH_MEMORY_USAGE",
            source="memory",
            subject="",
            attribute="usage_percent",
            value=88,
        )


def test_signal_requires_attribute():
    with pytest.raises(ValueError):
        Signal(
            signal_type="HIGH_MEMORY_USAGE",
            source="memory",
            subject="system_memory",
            attribute="",
            value=88,
        )


def test_signal_supports_different_value_types():
    numeric_signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    text_signal = Signal(
        signal_type="NETWORK_STATUS",
        source="network",
        subject="network_adapter",
        attribute="status",
        value="connected",
    )

    assert numeric_signal.value == 88
    assert text_signal.value == "connected"


def test_signal_preserves_semantic_identity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    assert signal.signal_type == "HIGH_MEMORY_USAGE"
    assert signal.source == "memory"
    assert signal.subject == "system_memory"
    assert signal.attribute == "usage_percent"
    assert signal.value == 88