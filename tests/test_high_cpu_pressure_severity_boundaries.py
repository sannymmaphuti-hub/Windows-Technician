from engine.high_cpu_pressure_rule import HighCpuPressureRule
from engine.signal import Signal


def create_cpu_signal(value):
    return Signal(
        signal_type="HIGH_CPU_USAGE",
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=value,
        strength="HIGH",
    )


def test_cpu_90_is_low_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(90))

    assert finding.severity == "LOW"


def test_cpu_94_is_low_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(94))

    assert finding.severity == "LOW"


def test_cpu_95_is_medium_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(95))

    assert finding.severity == "MEDIUM"


def test_cpu_98_is_medium_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(98))

    assert finding.severity == "MEDIUM"


def test_cpu_99_is_high_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(99))

    assert finding.severity == "HIGH"


def test_cpu_100_is_high_severity():
    rule = HighCpuPressureRule()

    finding = rule.create_finding(create_cpu_signal(100))

    assert finding.severity == "HIGH"