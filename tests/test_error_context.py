"""Tests for production error context."""

from datetime import datetime, timezone

import pytest

from packaging.error_context import (
    ErrorContext,
    create_error_context,
    error_context_to_dict,
)


def test_error_context_captures_exception_type():
    error = RuntimeError("diagnostic failed")

    context = create_error_context(
        error=error,
        component="diagnostics",
        operation="collect",
    )

    assert context.error_type == "RuntimeError"


def test_error_context_captures_message():
    error = RuntimeError("diagnostic failed")

    context = create_error_context(
        error=error,
        component="diagnostics",
        operation="collect",
    )

    assert context.message == "diagnostic failed"


def test_error_context_captures_component():
    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
    )

    assert context.component == "diagnostics"


def test_error_context_captures_operation():
    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
    )

    assert context.operation == "collect"


def test_error_context_generates_timezone_aware_timestamp():
    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
    )

    assert context.timestamp.tzinfo is not None


def test_explicit_timestamp_is_preserved():
    timestamp = datetime(
        2026,
        10,
        6,
        20,
        30,
        tzinfo=timezone.utc,
    )

    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
        timestamp=timestamp,
    )

    assert context.timestamp == timestamp


def test_error_context_requires_exception():
    with pytest.raises(TypeError):
        create_error_context(
            error="not an exception",
            component="diagnostics",
            operation="collect",
        )


def test_error_context_requires_component():
    with pytest.raises(ValueError):
        create_error_context(
            error=RuntimeError("failure"),
            component="",
            operation="collect",
        )


def test_error_context_requires_operation():
    with pytest.raises(ValueError):
        create_error_context(
            error=RuntimeError("failure"),
            component="diagnostics",
            operation="",
        )


def test_error_context_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError):
        ErrorContext(
            error_type="RuntimeError",
            message="failure",
            component="diagnostics",
            operation="collect",
            timestamp=datetime(2026, 10, 6),
        )


def test_error_context_requires_datetime():
    with pytest.raises(TypeError):
        ErrorContext(
            error_type="RuntimeError",
            message="failure",
            component="diagnostics",
            operation="collect",
            timestamp="2026-10-06",
        )


def test_error_context_to_dict_is_serializable():
    timestamp = datetime(
        2026,
        10,
        6,
        20,
        30,
        tzinfo=timezone.utc,
    )

    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
        timestamp=timestamp,
    )

    result = error_context_to_dict(context)

    assert result["error_type"] == "RuntimeError"
    assert result["message"] == "failure"
    assert result["component"] == "diagnostics"
    assert result["operation"] == "collect"
    assert result["timestamp"] == timestamp.isoformat()


def test_error_context_to_dict_requires_context():
    with pytest.raises(TypeError):
        error_context_to_dict("invalid")


def test_error_context_is_immutable():
    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
    )

    with pytest.raises(AttributeError):
        context.message = "changed"
