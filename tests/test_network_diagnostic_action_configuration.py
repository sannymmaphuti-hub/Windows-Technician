from engine.diagnostic_action_selection_orchestrator import (
    DiagnosticActionSelectionOrchestrator,
)
from engine.network_diagnostic_action_configuration import (
    create_network_diagnostic_action_orchestrator,
)


def test_network_action_configuration_returns_orchestrator():
    orchestrator = create_network_diagnostic_action_orchestrator()

    assert isinstance(
        orchestrator,
        DiagnosticActionSelectionOrchestrator,
    )


def test_network_action_configuration_selects_adapter_action():
    orchestrator = create_network_diagnostic_action_orchestrator()

    action = orchestrator.select("CHECK_NETWORK_ADAPTER")

    assert action is not None
    assert action.action_type == "COLLECT_NETWORK_ADAPTER_STATE"


def test_network_action_configuration_selects_gateway_action():
    orchestrator = create_network_diagnostic_action_orchestrator()

    action = orchestrator.select("CHECK_GATEWAY_REACHABILITY")

    assert action is not None
    assert action.action_type == "PING_DEFAULT_GATEWAY"


def test_network_action_configuration_selects_dns_action():
    orchestrator = create_network_diagnostic_action_orchestrator()

    action = orchestrator.select("CHECK_DNS_RESOLUTION")

    assert action is not None
    assert action.action_type == "TEST_DNS_RESOLUTION"


def test_network_action_configuration_selects_internet_action():
    orchestrator = create_network_diagnostic_action_orchestrator()

    action = orchestrator.select("CHECK_INTERNET_CONNECTIVITY")

    assert action is not None
    assert action.action_type == "TEST_INTERNET_CONNECTIVITY"


def test_network_action_configuration_has_no_action_for_unknown_decision():
    orchestrator = create_network_diagnostic_action_orchestrator()

    assert orchestrator.select("UNKNOWN_DECISION") is None