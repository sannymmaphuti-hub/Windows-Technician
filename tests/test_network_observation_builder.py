from engine.network_observation_builder import NetworkObservationBuilder
from engine.observation import Observation


def test_network_observation_builder_returns_observations():

    evidence = {
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

    observations = NetworkObservationBuilder().build(evidence)

    assert observations
    assert all(
        isinstance(observation, Observation)
        for observation in observations
    )


def test_network_observation_builder_detects_adapter_state():

    evidence = {
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
        }
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_adapter"
        and observation.attribute == "is_up"
        and observation.value is True
        for observation in observations
    )


def test_network_observation_builder_detects_ipv4_address():

    evidence = {
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
        }
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_adapter"
        and observation.attribute == "ipv4_address"
        and observation.value == "192.168.0.238"
        for observation in observations
    )


def test_network_observation_builder_detects_ipv4_classification():

    evidence = {
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
        }
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_adapter"
        and observation.attribute == "ipv4_classification"
        and observation.value == "PRIVATE"
        for observation in observations
    )


def test_network_observation_builder_detects_gateway_state():

    evidence = {
        "gateway": "192.168.0.1",
        "gateway_reachable": True,
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_gateway"
        and observation.attribute == "address"
        and observation.value == "192.168.0.1"
        for observation in observations
    )

    assert any(
        observation.subject == "network_gateway"
        and observation.attribute == "reachable"
        and observation.value is True
        for observation in observations
    )


def test_network_observation_builder_detects_internet_state():

    evidence = {
        "internet_reachable": False,
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_internet"
        and observation.attribute == "reachable"
        and observation.value is False
        for observation in observations
    )


def test_network_observation_builder_detects_dns_state():

    evidence = {
        "dns_working": False,
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert any(
        observation.subject == "network_dns"
        and observation.attribute == "working"
        and observation.value is False
        for observation in observations
    )


def test_network_observation_builder_handles_partial_evidence():

    evidence = {
        "internet_reachable": False,
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert len(observations) == 1

    observation = observations[0]

    assert observation.source == "network"
    assert observation.subject == "network_internet"
    assert observation.attribute == "reachable"
    assert observation.value is False


def test_network_observation_builder_does_not_create_diagnostic_conclusions():

    evidence = {
        "internet_reachable": False,
        "dns_working": False,
        "status": "WARNING",
        "findings": [
            {
                "severity": "WARNING",
                "category": "DNS",
                "message": "DNS hostname resolution failed.",
            }
        ],
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert all(
        observation.subject not in {
            "network_finding",
            "network_status",
        }
        for observation in observations
    )

    assert all(
        observation.attribute not in {
            "severity",
            "message",
            "diagnosis",
        }
        for observation in observations
    )


def test_network_observation_builder_handles_missing_active_adapter():

    evidence = {
        "active_adapter": None,
        "gateway": None,
        "gateway_reachable": False,
        "internet_reachable": False,
        "dns_working": False,
    }

    observations = NetworkObservationBuilder().build(evidence)

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


def test_network_observation_builder_uses_network_source():

    evidence = {
        "internet_reachable": True,
        "dns_working": True,
    }

    observations = NetworkObservationBuilder().build(evidence)

    assert all(
        observation.source == "network"
        for observation in observations
    )