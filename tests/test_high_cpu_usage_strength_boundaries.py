from engine.observation import Observation
from engine.high_cpu_usage_rule import HighCpuUsageRule


def make_cpu_observation(value):
    return Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=value,
    )


def test_cpu_usage_89_percent_does_not_match():
    rule = HighCpuUsageRule()

    assert rule.matches(make_cpu_observation(89)) is False


def test_cpu_usage_90_percent_produces_low_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(90))

    assert signal.strength == "LOW"


def test_cpu_usage_94_percent_produces_low_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(94))

    assert signal.strength == "LOW"


def test_cpu_usage_95_percent_produces_medium_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(95))

    assert signal.strength == "MEDIUM"


def test_cpu_usage_98_percent_produces_medium_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(98))

    assert signal.strength == "MEDIUM"


def test_cpu_usage_99_percent_produces_high_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(99))

    assert signal.strength == "HIGH"


def test_cpu_usage_100_percent_produces_high_strength():
    rule = HighCpuUsageRule()

    signal = rule.create_signal(make_cpu_observation(100))

    assert signal.strength == "HIGH"