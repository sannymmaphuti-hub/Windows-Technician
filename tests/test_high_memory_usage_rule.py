from engine.observation import Observation
from engine.signal import Signal
from engine.high_memory_usage_rule import HighMemoryUsageRule


def test_high_memory_usage_rule_matches_high_memory_observation():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    assert rule.matches(observation) is True


def test_high_memory_usage_rule_rejects_normal_memory_usage():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=45,
    )

    assert rule.matches(observation) is False


def test_high_memory_usage_rule_accepts_threshold_value():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=85,
    )

    assert rule.matches(observation) is True


def test_high_memory_usage_rule_rejects_value_below_threshold():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=84,
    )

    assert rule.matches(observation) is False


def test_high_memory_usage_rule_rejects_unrelated_observation():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=88,
    )

    assert rule.matches(observation) is False


def test_high_memory_usage_rule_creates_high_memory_signal():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = rule.create_signal(observation)

    assert isinstance(signal, Signal)
    assert signal.signal_type == "HIGH_MEMORY_USAGE"


def test_high_memory_usage_rule_preserves_observation_context():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = rule.create_signal(observation)

    assert signal.source == "memory"
    assert signal.subject == "system_memory"
    assert signal.attribute == "usage_percent"
    assert signal.value == 88


def test_high_memory_usage_rule_does_not_modify_observation():
    rule = HighMemoryUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    rule.create_signal(observation)

    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88