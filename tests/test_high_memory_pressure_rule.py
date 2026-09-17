from engine.finding import Finding
from engine.high_memory_pressure_rule import HighMemoryPressureRule
from engine.signal import Signal


def create_memory_signal(
    value=97,
    strength="HIGH",
    quality=None,
):
    return Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=value,
        strength=strength,
        quality=quality,
    )


def test_rule_matches_high_memory_usage_signal():
    rule = HighMemoryPressureRule()
    signal = create_memory_signal()

    assert rule.matches(signal) is True


def test_rule_does_not_match_unrelated_signal():
    rule = HighMemoryPressureRule()

    signal = Signal(
        signal_type="HIGH_CPU_USAGE",
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=97,
        strength="HIGH",
    )

    assert rule.matches(signal) is False


def test_rule_does_not_match_wrong_memory_attribute():
    rule = HighMemoryPressureRule()

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="available_percent",
        value=97,
        strength="HIGH",
    )

    assert rule.matches(signal) is False


def test_rule_creates_memory_pressure_finding():
    rule = HighMemoryPressureRule()
    signal = create_memory_signal()

    finding = rule.create_finding(signal)

    assert isinstance(finding, Finding)
    assert finding.finding_type == "MEMORY_PRESSURE"
    assert finding.category == "MEMORY"
    assert finding.description == "System memory pressure is high."


def test_rule_preserves_supporting_signal():
    rule = HighMemoryPressureRule()
    signal = create_memory_signal()

    finding = rule.create_finding(signal)

    assert finding.supporting_signals == [signal]


def test_rule_does_not_use_signal_strength_as_finding_severity():
    rule = HighMemoryPressureRule()

    signal = create_memory_signal(
        value=97,
        strength="HIGH",
    )

    finding = rule.create_finding(signal)

    assert finding.severity == "HIGH"


def test_rule_preserves_signal_quality_independently():
    rule = HighMemoryPressureRule()

    signal = create_memory_signal(
        value=97,
        strength="HIGH",
        quality="LOW",
    )

    finding = rule.create_finding(signal)

    assert finding.supporting_signals == [signal]
    assert signal.quality == "LOW"