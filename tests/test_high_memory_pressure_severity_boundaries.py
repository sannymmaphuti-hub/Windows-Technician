from engine.high_memory_pressure_rule import HighMemoryPressureRule
from engine.signal import Signal


def create_memory_signal(value):
    return Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=value,
        strength="HIGH",
    )


def test_memory_89_is_low_severity():
    rule = HighMemoryPressureRule()

    finding = rule.create_finding(create_memory_signal(89))

    assert finding.severity == "LOW"


def test_memory_90_is_medium_severity():
    rule = HighMemoryPressureRule()

    finding = rule.create_finding(create_memory_signal(90))

    assert finding.severity == "MEDIUM"


def test_memory_94_is_medium_severity():
    rule = HighMemoryPressureRule()

    finding = rule.create_finding(create_memory_signal(94))

    assert finding.severity == "MEDIUM"


def test_memory_95_is_high_severity():
    rule = HighMemoryPressureRule()

    finding = rule.create_finding(create_memory_signal(95))

    assert finding.severity == "HIGH"


def test_memory_100_is_high_severity():
    rule = HighMemoryPressureRule()

    finding = rule.create_finding(create_memory_signal(100))

    assert finding.severity == "HIGH"