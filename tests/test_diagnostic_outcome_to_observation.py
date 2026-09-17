import pytest

from engine.diagnostic_action_outcome import DiagnosticActionOutcome
from engine.observation import Observation


def create_outcome(evidence):
    return DiagnosticActionOutcome(
        action_type="PING_DEFAULT_GATEWAY",
        evidence=evidence,
    )


def test_translator_can_be_created():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    assert translator is not None


def test_translator_requires_diagnostic_action_outcome():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    with pytest.raises(ValueError, match="outcome must be a DiagnosticActionOutcome"):
        translator.translate({})


def test_gateway_reachability_true_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome(
        {
            "gateway_reachable": True,
        }
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "network_gateway"
    assert observation.attribute == "reachable"
    assert observation.value is True


def test_gateway_reachability_false_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome(
        {
            "gateway_reachable": False,
        }
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "network_gateway"
    assert observation.attribute == "reachable"
    assert observation.value is False


def test_translator_preserves_gateway_evidence_value():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome(
        {
            "gateway_reachable": True,
        }
    )

    observation = translator.translate(outcome)

    assert observation.value == outcome.evidence["gateway_reachable"]


def test_translator_does_not_create_diagnostic_conclusions():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome(
        {
            "gateway_reachable": True,
        }
    )

    observation = translator.translate(outcome)

    assert not hasattr(observation, "finding")
    assert not hasattr(observation, "root_cause")
    assert not hasattr(observation, "recommendation")
    assert not hasattr(observation, "remediation")


def test_translator_rejects_unsupported_evidence():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome(
        {
            "unknown_network_value": True,
        }
    )

    with pytest.raises(ValueError, match="Unsupported diagnostic evidence"):
        translator.translate(outcome)


def test_translator_rejects_empty_evidence():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = create_outcome({})

    with pytest.raises(ValueError, match="Unsupported diagnostic evidence"):
        translator.translate(outcome)

def test_dns_resolution_true_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_DNS_RESOLUTION",
        evidence={
            "dns_working": True,
        },
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "dns"
    assert observation.attribute == "resolution_working"
    assert observation.value is True


def test_dns_resolution_false_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_DNS_RESOLUTION",
        evidence={
            "dns_working": False,
        },
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "dns"
    assert observation.attribute == "resolution_working"
    assert observation.value is False


def test_internet_connectivity_true_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_INTERNET_CONNECTIVITY",
        evidence={
            "internet_reachable": True,
        },
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "internet"
    assert observation.attribute == "reachable"
    assert observation.value is True


def test_internet_connectivity_false_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="TEST_INTERNET_CONNECTIVITY",
        evidence={
            "internet_reachable": False,
        },
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "internet"
    assert observation.attribute == "reachable"
    assert observation.value is False

def test_network_adapter_state_becomes_observation():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    adapters = [
        {
            "name": "Wi-Fi",
            "is_up": True,
        }
    ]

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": adapters,
        },
    )

    observation = translator.translate(outcome)

    assert isinstance(observation, Observation)
    assert observation.subject == "network_adapter"
    assert observation.attribute == "state"
    assert observation.value == adapters


def test_network_adapter_state_preserves_adapter_evidence():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    adapters = [
        {
            "name": "Wi-Fi",
            "is_up": True,
            "ip_address": "192.168.1.10",
        },
        {
            "name": "Ethernet",
            "is_up": False,
        },
    ]

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": adapters,
        },
    )

    observation = translator.translate(outcome)

    assert observation.value == adapters


def test_network_adapter_state_does_not_become_a_finding():
    from engine.diagnostic_outcome_to_observation import (
        DiagnosticOutcomeToObservation,
    )

    translator = DiagnosticOutcomeToObservation()

    outcome = DiagnosticActionOutcome(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": False,
                }
            ],
        },
    )

    observation = translator.translate(outcome)

    assert not hasattr(observation, "finding")
    assert not hasattr(observation, "root_cause")
    assert not hasattr(observation, "recommendation")
    assert not hasattr(observation, "remediation")