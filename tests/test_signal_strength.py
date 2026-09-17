from engine.observation import Observation
from engine.high_cpu_usage_rule import HighCpuUsageRule


def test_signal_has_strength():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=91,
    )

    signal = rule.create_signal(observation)

    assert signal.strength is not None


def test_cpu_signal_strength_is_low_for_90_to_94_percent():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=92,
    )

    signal = rule.create_signal(observation)

    assert signal.strength == "LOW"


def test_cpu_signal_strength_is_medium_for_95_to_98_percent():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=96,
    )

    signal = rule.create_signal(observation)

    assert signal.strength == "MEDIUM"


def test_cpu_signal_strength_is_high_for_99_to_100_percent():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal = rule.create_signal(observation)

    assert signal.strength == "HIGH"


def test_signal_strength_is_exported_as_evidence():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal = rule.create_signal(observation)

    evidence = signal.to_evidence()

    assert evidence["strength"] == "HIGH"


def test_signal_strength_does_not_change_signal_identity():
    rule = HighCpuUsageRule()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal = rule.create_signal(observation)

    assert signal.signal_type == "HIGH_CPU_USAGE"
    assert signal.source == "cpu"
    assert signal.subject == "system_cpu"
    assert signal.attribute == "usage_percent"
    assert signal.value == 99