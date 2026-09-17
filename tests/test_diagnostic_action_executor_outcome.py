from engine.diagnostic_action import DiagnosticAction
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


def create_action():
    return DiagnosticAction(
        action_type="TEST_OPERATION",
        category="NETWORK",
        description="Run a diagnostic test.",
    )


def test_executor_returns_diagnostic_action_outcome():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: {
            "test_value": True,
        },
    )

    result = executor.execute(create_action())

    assert isinstance(result, DiagnosticActionOutcome)


def test_executor_outcome_contains_action_type():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: {
            "test_value": True,
        },
    )

    result = executor.execute(create_action())

    assert result.action_type == "TEST_OPERATION"


def test_executor_outcome_contains_evidence():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: {
            "test_value": True,
        },
    )

    result = executor.execute(create_action())

    assert result.evidence == {
        "test_value": True,
    }


def test_executor_preserves_empty_evidence():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: {},
    )

    result = executor.execute(create_action())

    assert isinstance(result, DiagnosticActionOutcome)
    assert result.evidence == {}


def test_executor_rejects_non_dictionary_operation_result():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: "invalid",
    )

    try:
        executor.execute(create_action())
    except ValueError as error:
        assert str(error) == (
            "diagnostic operation must return an evidence dictionary."
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid operation result."
        )


def test_executor_outcome_contains_no_diagnostic_conclusions():
    executor = DiagnosticActionExecutor()

    executor.register_operation(
        "TEST_OPERATION",
        lambda: {
            "test_value": True,
        },
    )

    result = executor.execute(create_action())

    result_data = result.to_dict()

    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data
    assert "remediation" not in result_data