from engine.observation import Observation
from engine.high_cpu_usage_rule import HighCpuUsageRule


def test_high_cpu_usage_rule_matches_high_cpu_observation():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    assert rule.matches(observation) is True


def test_high_cpu_usage_rule_rejects_normal_cpu_usage():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=45,
    )

    assert rule.matches(observation) is False


def test_high_cpu_usage_rule_accepts_threshold_value():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=90,
    )

    assert rule.matches(observation) is True


def test_high_cpu_usage_rule_rejects_value_below_threshold():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=89,
    )

    assert rule.matches(observation) is False


def test_high_cpu_usage_rule_rejects_unrelated_observation():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=95,
    )

    assert rule.matches(observation) is False


def test_high_cpu_usage_rule_creates_high_cpu_signal():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    signal = rule.create_signal(observation)

    assert signal.signal_type == "HIGH_CPU_USAGE"


def test_high_cpu_usage_rule_preserves_observation_context():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    signal = rule.create_signal(observation)

    assert signal.source == observation.source
    assert signal.subject == observation.subject
    assert signal.attribute == observation.attribute
    assert signal.value == observation.value


def test_high_cpu_usage_rule_does_not_modify_observation():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    original = observation.to_evidence()

    rule.create_signal(observation)

    assert observation.to_evidence() == original