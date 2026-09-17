from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal


def test_observation_to_signal_uses_high_memory_rule():
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


def test_observation_to_signal_still_rejects_normal_memory_usage():
    detector = ObservationToSignal()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=45,
    )

    signal = detector.detect(observation)

    assert signal is None


def test_observation_to_signal_still_preserves_signal_context():
    detector = ObservationToSignal()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = detector.detect(observation)

    assert signal.source == observation.source
    assert signal.subject == observation.subject
    assert signal.attribute == observation.attribute
    assert signal.value == observation.value


def test_observation_to_signal_still_ignores_unknown_observation():
    detector = ObservationToSignal()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="temperature_celsius",
        value=50,
    )

    signal = detector.detect(observation)

    assert signal is None