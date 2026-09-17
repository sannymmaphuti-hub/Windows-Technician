from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_selector import DiagnosticActionSelector


def test_selector_maps_network_adapter_decision():
    selector = DiagnosticActionSelector()

    action = selector.select("CHECK_NETWORK_ADAPTER")

    assert isinstance(action, DiagnosticAction)
    assert action.action_type == "COLLECT_NETWORK_ADAPTER_STATE"
    assert action.category == "NETWORK"


def test_selector_maps_gateway_decision():
    selector = DiagnosticActionSelector()

    action = selector.select("CHECK_GATEWAY_REACHABILITY")

    assert action.action_type == "PING_DEFAULT_GATEWAY"
    assert action.category == "NETWORK"


def test_selector_maps_dns_decision():
    selector = DiagnosticActionSelector()

    action = selector.select("CHECK_DNS_RESOLUTION")

    assert action.action_type == "TEST_DNS_RESOLUTION"
    assert action.category == "NETWORK"


def test_selector_maps_internet_decision():
    selector = DiagnosticActionSelector()

    action = selector.select("CHECK_INTERNET_CONNECTIVITY")

    assert action.action_type == "TEST_INTERNET_CONNECTIVITY"
    assert action.category == "NETWORK"


def test_selector_rejects_unknown_decision():
    selector = DiagnosticActionSelector()

    try:
        selector.select("UNKNOWN_DECISION")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_selector_rejects_empty_decision():
    selector = DiagnosticActionSelector()

    try:
        selector.select("")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_selector_rejects_non_string_decision():
    selector = DiagnosticActionSelector()

    try:
        selector.select(123)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")