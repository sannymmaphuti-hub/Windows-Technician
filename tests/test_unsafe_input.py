"""Tests for the production unsafe-input validation boundary."""

import pytest

from packaging.unsafe_input import (
    InputValidationError,
    ValidatedInput,
    validate_command_argument,
    validate_identifier,
    validate_machine_name,
    validate_remote_target,
    validate_service_name,
)


def test_valid_machine_name():
    result = validate_machine_name("TECH-PC01")

    assert isinstance(result, ValidatedInput)
    assert result.value == "TECH-PC01"
    assert result.input_type == "machine_name"


@pytest.mark.parametrize(
    "machine_name",
    [
        "",
        " ",
        " TECH-PC01",
        "TECH-PC01 ",
        "TECH/PC01",
        "TECH\\PC01",
        "TECH PC01",
        "TECH;PC01",
        "\x00TECH",
    ],
)
def test_invalid_machine_name_is_rejected(machine_name):
    with pytest.raises(InputValidationError):
        validate_machine_name(machine_name)


def test_machine_name_allows_standard_windows_characters():
    for value in (
        "PC-01",
        "PC_01",
        "PC.01",
        "SERVER01",
    ):
        assert validate_machine_name(value).value == value


def test_valid_identifier():
    result = validate_identifier("service.restart:01")

    assert result.value == "service.restart:01"
    assert result.input_type == "identifier"


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        " identifier",
        "identifier ",
        "identifier/value",
        "identifier\\value",
        "identifier value",
        "\x00identifier",
    ],
)
def test_invalid_identifier_is_rejected(identifier):
    with pytest.raises(InputValidationError):
        validate_identifier(identifier)


def test_valid_service_name():
    result = validate_service_name("WindowsUpdate")

    assert result.value == "WindowsUpdate"
    assert result.input_type == "service_name"


@pytest.mark.parametrize(
    "service_name",
    [
        "",
        " ",
        " WindowsUpdate",
        "WindowsUpdate ",
        "Windows/Update",
        "Windows\\Update",
        "Windows Update",
        "\x00WindowsUpdate",
    ],
)
def test_invalid_service_name_is_rejected(service_name):
    with pytest.raises(InputValidationError):
        validate_service_name(service_name)


@pytest.mark.parametrize(
    "argument",
    [
        "WindowsUpdate",
        "C:\\Windows",
        "service-name",
        "123",
        "--verbose",
    ],
)
def test_safe_command_arguments_are_accepted(argument):
    result = validate_command_argument(argument)

    assert result.value == argument
    assert result.input_type == "command_argument"


@pytest.mark.parametrize(
    "argument",
    [
        "",
        " ",
        "value&whoami",
        "value|whoami",
        "value;whoami",
        "value>file",
        "value<file",
        "value`whoami",
        "value\r\nwhoami",
        "\x00value",
    ],
)
def test_command_injection_markers_are_rejected(argument):
    with pytest.raises(InputValidationError):
        validate_command_argument(argument)


def test_valid_remote_target():
    result = validate_remote_target("TECH-PC01")

    assert result.value == "TECH-PC01"
    assert result.input_type == "remote_target"


@pytest.mark.parametrize(
    "target",
    [
        "",
        " ",
        " TECH-PC01",
        "TECH-PC01 ",
        "TECH PC01",
        "TECH/PC01",
        "TECH\\PC01",
        "TECH;PC01",
        "\x00TECH-PC01",
    ],
)
def test_invalid_remote_target_is_rejected(target):
    with pytest.raises(InputValidationError):
        validate_remote_target(target)


def test_non_string_values_are_rejected():
    with pytest.raises(InputValidationError):
        validate_machine_name(123)

    with pytest.raises(InputValidationError):
        validate_identifier(123)

    with pytest.raises(InputValidationError):
        validate_service_name(123)

    with pytest.raises(InputValidationError):
        validate_command_argument(123)

    with pytest.raises(InputValidationError):
        validate_remote_target(123)


def test_validated_input_is_immutable():
    result = validate_machine_name("TECH-PC01")

    with pytest.raises(AttributeError):
        result.value = "OTHER-PC"


def test_validated_input_rejects_invalid_constructor_values():
    with pytest.raises(ValueError):
        ValidatedInput(
            value="",
            input_type="machine_name",
        )

    with pytest.raises(ValueError):
        ValidatedInput(
            value="TECH-PC01",
            input_type="",
        )


def test_validation_does_not_execute_input():
    payload = "whoami"

    result = validate_command_argument(payload)

    assert result.value == payload
    assert result.input_type == "command_argument"
