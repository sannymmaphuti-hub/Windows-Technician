from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.network_diagnostic_operation_binding import (
    NetworkDiagnosticOperationBinding,
)
from engine.diagnostic_action_outcome import DiagnosticActionOutcome

def create_executor():
    executor = DiagnosticActionExecutor()
    binding = NetworkDiagnosticOperationBinding()
    binding.register(executor)
    return executor


def test_adapter_state_operation_is_registered():
    executor = create_executor()

    assert "COLLECT_NETWORK_ADAPTER_STATE" in executor.operations


def test_dns_operation_is_registered():
    executor = create_executor()

    assert "TEST_DNS_RESOLUTION" in executor.operations


def test_internet_operation_is_registered():
    executor = create_executor()

    assert "TEST_INTERNET_CONNECTIVITY" in executor.operations


def test_adapter_state_operation_is_callable():
    executor = create_executor()

    assert callable(
        executor.operations["COLLECT_NETWORK_ADAPTER_STATE"]
    )


def test_dns_operation_is_callable():
    executor = create_executor()

    assert callable(
        executor.operations["TEST_DNS_RESOLUTION"]
    )


def test_internet_operation_is_callable():
    executor = create_executor()

    assert callable(
        executor.operations["TEST_INTERNET_CONNECTIVITY"]
    )


def test_adapter_state_action_returns_evidence():
    executor = create_executor()

    action = DiagnosticAction(
        action_type="COLLECT_NETWORK_ADAPTER_STATE",
        category="NETWORK",
        description="Collect the current network adapter state.",
    )

    outcome = executor.execute(action)

    assert isinstance(
        outcome,
        DiagnosticActionOutcome,
    )
    assert "adapters" in outcome.evidence


def test_dns_action_returns_evidence():
    executor = create_executor()

    action = DiagnosticAction(
        action_type="TEST_DNS_RESOLUTION",
        category="NETWORK",
        description="Check whether DNS resolution is working.",
    )

    outcome = executor.execute(action)

    assert isinstance(
        outcome,
        DiagnosticActionOutcome,
    )
    assert "dns_working" in outcome.evidence


def test_internet_action_returns_evidence():
    executor = create_executor()

    action = DiagnosticAction(
        action_type="TEST_INTERNET_CONNECTIVITY",
        category="NETWORK",
        description="Check whether Internet connectivity is available.",
    )

    outcome = executor.execute(action)

    assert isinstance(
        outcome,
        DiagnosticActionOutcome,
    )
    assert "internet_reachable" in outcome.evidence


def test_all_network_operations_are_registered_together():
    executor = create_executor()

    expected_actions = {
        "PING_DEFAULT_GATEWAY",
        "COLLECT_NETWORK_ADAPTER_STATE",
        "TEST_DNS_RESOLUTION",
        "TEST_INTERNET_CONNECTIVITY",
    }

    assert expected_actions.issubset(executor.operations.keys())