from engine.finding import Finding
from engine.high_cpu_pressure_rule import HighCpuPressureRule
from engine.signal import Signal


def create_cpu_signal(
    value=99,
    strength="HIGH",
    quality=None,
):
    return Signal(
        signal_type="HIGH_CPU_USAGE",
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=value,
        strength=strength,
        quality=quality,
    )


def test_rule_matches_high_cpu_usage_signal():
    rule = HighCpuPressureRule()
    signal = create_cpu_signal()

    assert rule.matches(signal) is True


def test_rule_does_not_match_unrelated_signal():
    rule = HighCpuPressureRule()

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=99,
        strength="HIGH",
    )

    assert rule.matches(signal) is False


def test_rule_does_not_match_wrong_cpu_attribute():
    rule = HighCpuPressureRule()

    signal = Signal(
        signal_type="HIGH_CPU_USAGE",
        source="cpu",
        subject="system_cpu",
        attribute="temperature",
        value=99,
        strength="HIGH",
    )

    assert rule.matches(signal) is False


def test_rule_creates_cpu_pressure_finding():
    rule = HighCpuPressureRule()
    signal = create_cpu_signal()

    finding = rule.create_finding(signal)

    assert isinstance(finding, Finding)
    assert finding.finding_type == "CPU_PRESSURE"
    assert finding.category == "CPU"
    assert finding.description == "System CPU pressure is high."


def test_rule_preserves_supporting_signal():
    rule = HighCpuPressureRule()
    signal = create_cpu_signal()

    finding = rule.create_finding(signal)

    assert finding.supporting_signals == [signal]


def test_rule_determines_finding_severity_independently():
    rule = HighCpuPressureRule()

    signal = create_cpu_signal(
        value=99,
        strength="HIGH",
    )

    finding = rule.create_finding(signal)

    assert finding.severity == "HIGH"


def test_rule_preserves_signal_quality_independently():
    rule = HighCpuPressureRule()

    signal = create_cpu_signal(
        value=99,
        strength="HIGH",
        quality="LOW",
    )

    finding = rule.create_finding(signal)

    assert finding.supporting_signals == [signal]
    assert signal.quality == "LOW"