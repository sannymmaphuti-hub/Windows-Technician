from engine.signal import Signal


def test_signal_strength_does_not_create_severity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=98,
        strength="HIGH",
    )

    assert not hasattr(signal, "severity")


def test_signal_does_not_expose_severity_as_strength():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=98,
        strength="HIGH",
    )

    assert signal.strength == "HIGH"


def test_signal_evidence_contains_strength_but_not_severity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=98,
        strength="HIGH",
    )

    evidence = signal.to_evidence()

    assert evidence["strength"] == "HIGH"
    assert "severity" not in evidence


def test_low_strength_does_not_mean_low_severity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=85,
        strength="LOW",
    )

    assert signal.strength == "LOW"
    assert not hasattr(signal, "severity")


def test_high_strength_does_not_mean_high_severity():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=98,
        strength="HIGH",
    )

    assert signal.strength == "HIGH"
    assert not hasattr(signal, "severity")