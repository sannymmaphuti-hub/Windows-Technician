from engine.observation import Observation
from engine.high_memory_usage_rule import HighMemoryUsageRule


def make_memory_observation(value):
    return Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=value,
    )


def test_memory_usage_84_percent_does_not_match():
    rule = HighMemoryUsageRule()

    assert rule.matches(make_memory_observation(84)) is False


def test_memory_usage_85_percent_produces_low_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(85))

    assert signal.strength == "LOW"


def test_memory_usage_89_percent_produces_low_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(89))

    assert signal.strength == "LOW"


def test_memory_usage_90_percent_produces_medium_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(90))

    assert signal.strength == "MEDIUM"


def test_memory_usage_94_percent_produces_medium_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(94))

    assert signal.strength == "MEDIUM"


def test_memory_usage_95_percent_produces_high_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(95))

    assert signal.strength == "HIGH"


def test_memory_usage_100_percent_produces_high_strength():
    rule = HighMemoryUsageRule()

    signal = rule.create_signal(make_memory_observation(100))

    assert signal.strength == "HIGH"