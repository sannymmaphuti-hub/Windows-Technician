from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


def create_action():
    return DiagnosticAction(
        action_type="PING_DEFAULT_GATEWAY",
        category="NETWORK",
        description="Check whether the default gateway is reachable.",
    )


def test_executor_can_be_created():
    executor = DiagnosticActionExecutor()

    assert executor is not None


def test_executor_requires_diagnostic_action():
    executor = DiagnosticActionExecutor()

    try:
        executor.execute(None)
    except ValueError as error:
        assert str(error) == (
            "action must be a DiagnosticAction."
        )
    else:
        raise AssertionError(
            "Expected ValueError for missing diagnostic action."
        )


def test_executor_rejects_non_diagnostic_action():
    executor = DiagnosticActionExecutor()

    try:
        executor.execute("PING_DEFAULT_GATEWAY")
    except ValueError as error:
        assert str(error) == (
            "action must be a DiagnosticAction."
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid diagnostic action."
        )


def test_executor_returns_diagnostic_action_outcome():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        lambda: {
            "gateway_reachable": True,
        },
    )

    result = executor.execute(create_action())

    assert isinstance(result, DiagnosticActionOutcome)
    assert result.evidence == {
        "gateway_reachable": True,
    }


def test_executor_rejects_unsupported_action():
    executor = DiagnosticActionExecutor()

    try:
        executor.execute(create_action())
    except ValueError as error:
        assert str(error) == (
            "No operation registered for diagnostic action: "
            "PING_DEFAULT_GATEWAY."
        )
    else:
        raise AssertionError(
            "Expected ValueError for unsupported diagnostic action."
        )


def test_executor_does_not_return_diagnostic_conclusions():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "PING_DEFAULT_GATEWAY",
        lambda: {
            "gateway_reachable": True,
        },
    )

    result = executor.execute(create_action())
    result_data = result.to_dict()

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data