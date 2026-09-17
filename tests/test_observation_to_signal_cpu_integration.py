from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal


def test_observation_to_signal_detects_high_cpu_usage():
    detector = ObservationToSignal()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_CPU_USAGE"


def test_observation_to_signal_rejects_normal_cpu_usage():
    detector = ObservationToSignal()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=45,
    )

    signal = detector.detect(observation)

    assert signal is None


def test_observation_to_signal_preserves_cpu_signal_context():
    detector = ObservationToSignal()

    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    signal = detector.detect(observation)

    assert signal.source == observation.source
    assert signal.subject == observation.subject
    assert signal.attribute == observation.attribute
    assert signal.value == observation.value


def test_observation_to_signal_still_detects_high_memory_after_cpu_rule_added():
    detector = ObservationToSignal()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_MEMORY_USAGE"