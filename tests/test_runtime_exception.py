"""Tests for runtime exception containment."""

import pytest

from packaging.runtime_exception import (
    RuntimeFailure,
    RuntimeResult,
    execute_runtime_operation,
)


def test_successful_operation_returns_value():
    result = execute_runtime_operation(
        "calculate",
        lambda: 42,
    )

    assert result.succeeded is True
    assert result.value == 42
    assert result.failure is None


def test_runtime_exception_is_captured():
    def failing_operation():
        raise RuntimeError("operation failed")

    result = execute_runtime_operation(
        "diagnostic operation",
        failing_operation,
    )

    assert result.succeeded is False
    assert result.failure is not None
    assert result.failure.error_type == "RuntimeError"
    assert result.failure.message == "operation failed"
    assert result.failure.operation == "diagnostic operation"


def test_runtime_exception_does_not_escape_boundary():
    def failing_operation():
        raise ValueError("unexpected failure")

    result = execute_runtime_operation(
        "test operation",
        failing_operation,
    )

    assert result.succeeded is False


def test_operation_name_is_required():
    with pytest.raises(ValueError):
        execute_runtime_operation(
            "",
            lambda: None,
        )


def test_operation_callable_is_required():
    with pytest.raises(TypeError):
        execute_runtime_operation(
            "operation",
            "not callable",
        )


def test_runtime_failure_requires_error_type():
    with pytest.raises(ValueError):
        RuntimeFailure(
            error_type="",
            message="failure",
            operation="operation",
        )


def test_runtime_failure_requires_message():
    with pytest.raises(ValueError):
        RuntimeFailure(
            error_type="RuntimeError",
            message="",
            operation="operation",
        )


def test_runtime_failure_requires_operation():
    with pytest.raises(ValueError):
        RuntimeFailure(
            error_type="RuntimeError",
            message="failure",
            operation="",
        )


def test_successful_runtime_result_cannot_have_failure():
    with pytest.raises(ValueError):
        RuntimeResult(
            succeeded=True,
            value=42,
            failure=RuntimeFailure(
                error_type="RuntimeError",
                message="failure",
                operation="operation",
            ),
        )


def test_failed_runtime_result_requires_failure():
    with pytest.raises(ValueError):
        RuntimeResult(succeeded=False)


def test_runtime_result_is_immutable():
    result = execute_runtime_operation(
        "operation",
        lambda: "ok",
    )

    with pytest.raises(AttributeError):
        result.succeeded = False
