from engine.high_cpu_usage_rule import HighCpuUsageRule
from engine.high_memory_usage_rule import HighMemoryUsageRule
from engine.observation import Observation


def test_cpu_signal_quality_is_not_derived_from_signal_strength():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal = HighCpuUsageRule().create_signal(observation)

    assert signal.strength == "HIGH"
    assert signal.quality is None


def test_memory_signal_quality_is_not_derived_from_signal_strength():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
    )

    signal = HighMemoryUsageRule().create_signal(observation)

    assert signal.strength == "HIGH"
    assert signal.quality is None


def test_cpu_low_strength_does_not_imply_low_quality():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=90,
    )

    signal = HighCpuUsageRule().create_signal(observation)

    assert signal.strength == "LOW"
    assert signal.quality is None


def test_memory_low_strength_does_not_imply_low_quality():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=85,
    )

    signal = HighMemoryUsageRule().create_signal(observation)

    assert signal.strength == "LOW"
    assert signal.quality is None


def test_signal_quality_remains_independent_from_signal_strength():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal = HighCpuUsageRule().create_signal(observation)

    signal.quality = "LOW"

    assert signal.strength == "HIGH"
    assert signal.quality == "LOW"