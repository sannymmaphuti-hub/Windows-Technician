from engine.cpu_observation_builder import CPUObservationBuilder
from engine.evidence_builder import EvidenceBuilder
from engine.memory_observation_builder import MemoryObservationBuilder
from engine.observation import Observation
from engine.observation_builder import ObservationBuilder


def test_observation_builder_integrates_with_evidence_builder():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "CPU",
        {
            "usage_percent": 25,
            "physical_cores": 2,
            "logical_processors": 4,
            "frequency_mhz": 2400
        }
    )

    evidence_builder.add_category(
        "MEMORY",
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 8
    assert all(
        isinstance(observation, Observation)
        for observation in observations
    )


def test_observation_builder_integrates_with_partial_evidence():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "MEMORY",
        {
            "usage_percent": 88
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 1

    observation = observations[0]

    assert observation.source == "memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88


def test_observation_builder_ignores_unregistered_evidence_categories():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "CPU",
        {
            "usage_percent": 25
        }
    )

    evidence_builder.add_category(
        "UNKNOWN_CATEGORY",
        {
            "some_value": 123
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 1

    observation = observations[0]

    assert observation.source == "cpu"
    assert observation.attribute == "usage_percent"
    assert observation.value == 25

def test_observation_builder_integrates_network_evidence():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "NETWORK",
        {
            "active_adapter": {
                "name": "Wi-Fi",
                "is_up": True,
                "addresses": [
                    {
                        "type": "IPv4",
                        "address": "192.168.0.238",
                        "classification": "PRIVATE",
                    }
                ],
            },
            "gateway": "192.168.0.1",
            "gateway_reachable": True,
            "internet_reachable": False,
            "dns_working": False,
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 7
    assert all(
        isinstance(observation, Observation)
        for observation in observations
    )


def test_observation_builder_preserves_network_observation_values():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "NETWORK",
        {
            "active_adapter": {
                "name": "Wi-Fi",
                "is_up": True,
                "addresses": [
                    {
                        "type": "IPv4",
                        "address": "192.168.0.238",
                        "classification": "PRIVATE",
                    }
                ],
            },
            "gateway": "192.168.0.1",
            "gateway_reachable": True,
            "internet_reachable": False,
            "dns_working": False,
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_gateway"
        and observation.attribute == "reachable"
        and observation.value is True
        for observation in observations
    )

    assert any(
        observation.subject == "network_internet"
        and observation.attribute == "reachable"
        and observation.value is False
        for observation in observations
    )

    assert any(
        observation.subject == "network_dns"
        and observation.attribute == "working"
        and observation.value is False
        for observation in observations
    )


def test_observation_builder_still_preserves_cpu_and_memory_behavior():

    evidence_builder = EvidenceBuilder()

    evidence_builder.add_category(
        "CPU",
        {
            "usage_percent": 25,
        }
    )

    evidence_builder.add_category(
        "MEMORY",
        {
            "usage_percent": 88,
        }
    )

    evidence_builder.add_category(
        "NETWORK",
        {
            "internet_reachable": False,
        }
    )

    evidence = evidence_builder.build()

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 3

    assert observations[0].source == "cpu"
    assert observations[1].source == "memory"
    assert observations[2].source == "network"