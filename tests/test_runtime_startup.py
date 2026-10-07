"""Tests for the runtime startup reliability boundary."""

import pytest

from packaging.runtime_startup import (
    StartupFailure,
    StartupResult,
    execute_startup,
)


def test_successful_startup_returns_success():
    result = execute_startup(lambda: None)

    assert result.succeeded is True
    assert result.failure is None


def test_startup_exception_is_captured():
    def failing_startup():
        raise RuntimeError("startup exploded")

    result = execute_startup(failing_startup)

    assert result.succeeded is False
    assert result.failure is not None
    assert result.failure.error_type == "RuntimeError"
    assert result.failure.message == "startup exploded"


def test_startup_failure_does_not_escape_boundary():
    def failing_startup():
        raise ValueError("invalid startup state")

    result = execute_startup(failing_startup)

    assert result.succeeded is False


def test_startup_callable_must_be_callable():
    with pytest.raises(TypeError):
        execute_startup("not callable")


def test_startup_failure_requires_error_type():
    with pytest.raises(ValueError):
        StartupFailure(
            error_type="",
            message="failure",
        )


def test_startup_failure_requires_message():
    with pytest.raises(ValueError):
        StartupFailure(
            error_type="RuntimeError",
            message="",
        )


def test_successful_result_cannot_have_failure():
    with pytest.raises(ValueError):
        StartupResult(
            succeeded=True,
            failure=StartupFailure(
                error_type="RuntimeError",
                message="failure",
            ),
        )


def test_failed_result_requires_failure():
    with pytest.raises(ValueError):
        StartupResult(succeeded=False)


def test_startup_result_is_immutable():
    result = execute_startup(lambda: None)

    with pytest.raises(AttributeError):
        result.succeeded = False
