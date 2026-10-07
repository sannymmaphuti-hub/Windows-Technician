"""Tests for the production sensitive-information protection boundary."""

import pytest

from packaging.sensitive_information import (
    RedactionResult,
    SensitiveDataType,
    contains_sensitive_information,
    redact_sensitive_information,
    sanitize_for_logging,
)


def test_plain_text_is_not_redacted():
    result = redact_sensitive_information(
        "Windows Technician diagnostic completed."
    )

    assert result.value == "Windows Technician diagnostic completed."
    assert not result.redacted
    assert result.detected_types == ()


@pytest.mark.parametrize(
    "payload, expected_type",
    [
        (
            "password=SuperSecret123",
            SensitiveDataType.PASSWORD,
        ),
        (
            "passwd:SuperSecret123",
            SensitiveDataType.PASSWORD,
        ),
        (
            "pwd = SuperSecret123",
            SensitiveDataType.PASSWORD,
        ),
        (
            "token=abc123",
            SensitiveDataType.TOKEN,
        ),
        (
            "api_key=abc123",
            SensitiveDataType.API_KEY,
        ),
        (
            "api-key:abc123",
            SensitiveDataType.API_KEY,
        ),
        (
            "secret=hidden-value",
            SensitiveDataType.SECRET,
        ),
        (
            "connection_string=Server=db;Password=secret",
            SensitiveDataType.CONNECTION_STRING,
        ),
        (
            "Authorization: Bearer abc123",
            SensitiveDataType.AUTHORIZATION_HEADER,
        ),
        (
            "-----BEGIN PRIVATE KEY-----\n"
            "SECRET-MATERIAL\n"
            "-----END PRIVATE KEY-----",
            SensitiveDataType.PRIVATE_KEY,
        ),
    ],
)
def test_sensitive_values_are_detected_and_redacted(
    payload,
    expected_type,
):
    result = redact_sensitive_information(payload)

    assert result.redacted
    assert expected_type in result.detected_types
    assert "SuperSecret123" not in result.value
    assert "abc123" not in result.value
    assert "hidden-value" not in result.value
    assert "SECRET-MATERIAL" not in result.value


def test_password_value_is_replaced():
    result = redact_sensitive_information(
        "password=SuperSecret123"
    )

    assert result.value == "password=[REDACTED]"
    assert result.redacted


def test_token_value_is_replaced():
    result = redact_sensitive_information(
        "token=abc123"
    )

    assert result.value == "token=[REDACTED]"


def test_api_key_value_is_replaced():
    result = redact_sensitive_information(
        "api_key=abc123"
    )

    assert result.value == "api_key=[REDACTED]"


def test_private_key_is_replaced():
    result = redact_sensitive_information(
        "-----BEGIN PRIVATE KEY-----\n"
        "SECRET-MATERIAL\n"
        "-----END PRIVATE KEY-----"
    )

    assert result.value == "[REDACTED PRIVATE KEY]"
    assert result.redacted


def test_multiple_sensitive_types_are_detected():
    result = redact_sensitive_information(
        "password=one token=two api_key=three"
    )

    assert result.redacted
    assert SensitiveDataType.PASSWORD in result.detected_types
    assert SensitiveDataType.TOKEN in result.detected_types
    assert SensitiveDataType.API_KEY in result.detected_types


def test_contains_sensitive_information_returns_true():
    assert contains_sensitive_information(
        "token=secret-token"
    )


def test_contains_sensitive_information_returns_false():
    assert not contains_sensitive_information(
        "diagnostic status: healthy"
    )


def test_logging_sanitizer_returns_redacted_value():
    result = sanitize_for_logging(
        "operation completed token=abc123"
    )

    assert result == "operation completed token=[REDACTED]"
    assert "abc123" not in result


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ordinary text",
        "Windows Technician",
        "CPU usage: 42%",
        "memory usage: 61%",
    ],
)
def test_safe_values_are_preserved(value):
    result = redact_sensitive_information(value)

    assert result.value == value
    assert not result.redacted


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        object(),
    ],
)
def test_non_string_values_are_rejected(value):
    with pytest.raises(TypeError):
        redact_sensitive_information(value)


def test_redaction_result_is_immutable():
    result = redact_sensitive_information(
        "password=secret"
    )

    with pytest.raises(AttributeError):
        result.value = "changed"


def test_redaction_result_rejects_invalid_detected_types():
    with pytest.raises(TypeError):
        RedactionResult(
            value="safe",
            redacted=False,
            detected_types=("PASSWORD",),
        )


def test_redaction_result_rejects_duplicate_types():
    with pytest.raises(ValueError):
        RedactionResult(
            value="safe",
            redacted=True,
            detected_types=(
                SensitiveDataType.PASSWORD,
                SensitiveDataType.PASSWORD,
            ),
        )


def test_redaction_does_not_modify_original_input():
    original = "password=secret"

    result = redact_sensitive_information(original)

    assert original == "password=secret"
    assert result.value == "password=[REDACTED]"


def test_sensitive_value_is_not_present_after_sanitization():
    payload = "Authorization: Bearer very-secret-token"

    sanitized = sanitize_for_logging(payload)

    assert "very-secret-token" not in sanitized
    assert "[REDACTED]" in sanitized
