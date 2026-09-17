import pytest

from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal


def test_high_memory_observation_creates_high_memory_signal():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_MEMORY_USAGE"


def test_high_memory_signal_preserves_observation_context():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal.source == "memory"
    assert signal.subject == "system_memory"
    assert signal.attribute == "usage_percent"
    assert signal.value == 88


def test_normal_memory_usage_does_not_create_high_memory_signal():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=45,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_memory_usage_at_threshold_creates_signal():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=85,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_MEMORY_USAGE"


def test_observation_below_threshold_does_not_create_signal():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=84,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_unknown_observation_does_not_create_signal():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="temperature_celsius",
        value=50,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_detector_does_not_modify_observation():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    detector = ObservationToSignal()

    detector.detect(observation)

    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88

def test_disconnected_network_adapter_creates_signal():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=False,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "NETWORK_ADAPTER_DISCONNECTED"


def test_unreachable_gateway_creates_signal():
    observation = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=False,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "DEFAULT_GATEWAY_UNREACHABLE"


def test_failed_dns_creates_signal():
    observation = Observation(
        source="network",
        subject="network_dns",
        attribute="working",
        value=False,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "DNS_RESOLUTION_FAILED"


def test_unreachable_internet_creates_signal():
    observation = Observation(
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=False,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "INTERNET_UNREACHABLE"


def test_healthy_network_adapter_does_not_create_signal():
    observation = Observation(
        source="network",
        subject="network_adapter",
        attribute="is_up",
        value=True,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_reachable_gateway_does_not_create_signal():
    observation = Observation(
        source="network",
        subject="network_gateway",
        attribute="reachable",
        value=True,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_working_dns_does_not_create_signal():
    observation = Observation(
        source="network",
        subject="network_dns",
        attribute="working",
        value=True,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_reachable_internet_does_not_create_signal():
    observation = Observation(
        source="network",
        subject="network_internet",
        attribute="reachable",
        value=True,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is None


def test_existing_memory_signal_detection_still_works():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_MEMORY_USAGE"


def test_existing_cpu_signal_detection_still_works():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=95,
    )

    detector = ObservationToSignal()

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "HIGH_CPU_USAGE"