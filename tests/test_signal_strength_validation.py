import pytest

from engine.signal import Signal


def test_signal_accepts_low_strength():
    signal = Signal(
        signal_type="TEST_SIGNAL",
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=1,
        strength="LOW",
    )

    assert signal.strength == "LOW"


def test_signal_accepts_medium_strength():
    signal = Signal(
        signal_type="TEST_SIGNAL",
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=1,
        strength="MEDIUM",
    )

    assert signal.strength == "MEDIUM"


def test_signal_accepts_high_strength():
    signal = Signal(
        signal_type="TEST_SIGNAL",
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=1,
        strength="HIGH",
    )

    assert signal.strength == "HIGH"


def test_signal_rejects_invalid_strength():
    with pytest.raises(ValueError):
        Signal(
            signal_type="TEST_SIGNAL",
            source="test",
            subject="test_subject",
            attribute="test_attribute",
            value=1,
            strength="EXTREME",
        )


def test_signal_accepts_no_strength_for_backward_compatibility():
    signal = Signal(
        signal_type="TEST_SIGNAL",
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=1,
    )

    assert signal.strength is None