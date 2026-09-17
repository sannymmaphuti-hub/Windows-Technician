from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


def test_executor_can_register_diagnostic_operation():
    executor = DiagnosticActionExecutor()

    def operation():
        return {"gateway_reachable": True}

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        operation,
    )


def test_executor_rejects_invalid_action_type_during_registration():
    executor = DiagnosticActionExecutor()

    def operation():
        return {}

    try:
        executor.register_operation("", operation)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_executor_rejects_non_callable_operation():
    executor = DiagnosticActionExecutor()

    try:
        executor.register_operation(
            "PING_DEFAULT_GATEWAY",
            "not callable",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_registered_operation_is_executed():
    executor = DiagnosticActionExecutor()

    def operation():
        return {"gateway_reachable": True}

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        operation,
    )

    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    outcome = executor.execute(action)

    assert isinstance(outcome, DiagnosticActionOutcome)
    assert outcome.action_type == "PING_DEFAULT_GATEWAY"
    assert outcome.evidence == {
        "gateway_reachable": True,
    }


def test_registered_operation_must_return_evidence_dictionary():
    executor = DiagnosticActionExecutor()

    def operation():
        return "not evidence"

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        operation,
    )

    action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    try:
        executor.execute(action)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_executor_can_register_multiple_operations():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        lambda: {"gateway_reachable": True},
    )

    executor.register_operation(
        "TEST_DNS_RESOLUTION",
        lambda: {"dns_working": True},
    )

    gateway_action = DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )

    dns_action = DiagnosticAction(
        action_type="TEST_DNS_RESOLUTION",
        category="NETWORK",
        description="Check whether DNS resolution is working.",
    )

    gateway_outcome = executor.execute(gateway_action)
    dns_outcome = executor.execute(dns_action)

    assert isinstance(
        gateway_outcome,
        DiagnosticActionOutcome,
    )
    assert gateway_outcome.evidence == {
        "gateway_reachable": True,
    }

    assert isinstance(
        dns_outcome,
        DiagnosticActionOutcome,
    )
    assert dns_outcome.evidence == {
        "dns_working": True,
    }