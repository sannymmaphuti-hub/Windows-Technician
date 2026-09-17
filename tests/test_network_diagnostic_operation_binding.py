from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.network_diagnostic_operation_binding import (
    NetworkDiagnosticOperationBinding,
)
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


def test_network_binding_can_be_created():
    binding = NetworkDiagnosticOperationBinding()

    assert binding is not None


def test_network_binding_registers_gateway_operation():
    executor = DiagnosticActionExecutor()
    binding = NetworkDiagnosticOperationBinding()

    binding.register(executor)

    assert "PING_DEFAULT_GATEWAY" in executor.operations


def test_gateway_operation_is_callable():
    executor = DiagnosticActionExecutor()
    binding = NetworkDiagnosticOperationBinding()

    binding.register(executor)

    operation = executor.operations["PING_DEFAULT_GATEWAY"]

    assert callable(operation)


def test_gateway_action_can_be_executed_through_binding():
    executor = DiagnosticActionExecutor()
    binding = NetworkDiagnosticOperationBinding()

    binding.register(executor)

    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    outcome = executor.execute(action)

    assert isinstance(
        outcome,
        DiagnosticActionOutcome,
    )
    assert outcome.action_type == "PING_DEFAULT_GATEWAY"


def test_gateway_operation_returns_gateway_evidence():
    executor = DiagnosticActionExecutor()
    binding = NetworkDiagnosticOperationBinding()

    binding.register(executor)

    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    outcome = executor.execute(action)

    assert isinstance(
        outcome,
        DiagnosticActionOutcome,
    )
    assert "gateway_reachable" in outcome.evidence

def test_binding_requires_executor():
    binding = NetworkDiagnosticOperationBinding()

    try:
        binding.register(None)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")