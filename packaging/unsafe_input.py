"""Production unsafe-input validation boundary."""

from dataclasses import dataclass
import re


_MACHINE_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,62}$"
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)

_SERVICE_NAME_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$"
)

_FORBIDDEN_COMMAND_MARKERS = (
    "&",
    "|",
    ";",
    ">",
    "<",
    "`",
    "\r",
    "\n",
)


class InputValidationError(ValueError):
    """Raised when untrusted input violates a security boundary."""


@dataclass(frozen=True)
class ValidatedInput:
    """Validated input that has crossed the unsafe-input boundary."""

    value: str
    input_type: str

    def __post_init__(self):
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("value must be a non-empty string.")

        if not isinstance(self.input_type, str) or not self.input_type.strip():
            raise ValueError("input_type must be a non-empty string.")


def _validate_string(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise InputValidationError(
            f"{field_name} must be a string."
        )

    if not value.strip():
        raise InputValidationError(
            f"{field_name} cannot be empty."
        )

    if value != value.strip():
        raise InputValidationError(
            f"{field_name} cannot contain surrounding whitespace."
        )

    if "\x00" in value:
        raise InputValidationError(
            f"{field_name} cannot contain null bytes."
        )

    return value


def validate_machine_name(
    machine_name: str,
) -> ValidatedInput:
    value = _validate_string(
        machine_name,
        "machine_name",
    )

    if not _MACHINE_NAME_PATTERN.fullmatch(value):
        raise InputValidationError(
            "machine_name contains invalid characters."
        )

    return ValidatedInput(
        value=value,
        input_type="machine_name",
    )


def validate_identifier(
    identifier: str,
) -> ValidatedInput:
    value = _validate_string(
        identifier,
        "identifier",
    )

    if not _IDENTIFIER_PATTERN.fullmatch(value):
        raise InputValidationError(
            "identifier contains invalid characters."
        )

    return ValidatedInput(
        value=value,
        input_type="identifier",
    )


def validate_service_name(
    service_name: str,
) -> ValidatedInput:
    value = _validate_string(
        service_name,
        "service_name",
    )

    if not _SERVICE_NAME_PATTERN.fullmatch(value):
        raise InputValidationError(
            "service_name contains invalid characters."
        )

    return ValidatedInput(
        value=value,
        input_type="service_name",
    )


def validate_command_argument(
    argument: str,
) -> ValidatedInput:
    """Validate one argument without interpreting it as a shell command."""

    value = _validate_string(
        argument,
        "argument",
    )

    if any(marker in value for marker in _FORBIDDEN_COMMAND_MARKERS):
        raise InputValidationError(
            "argument contains command-injection markers."
        )

    return ValidatedInput(
        value=value,
        input_type="command_argument",
    )


def validate_remote_target(
    target: str,
) -> ValidatedInput:
    """Validate a remote target without executing or resolving it."""

    value = _validate_string(
        target,
        "remote_target",
    )

    if not _MACHINE_NAME_PATTERN.fullmatch(value):
        raise InputValidationError(
            "remote_target contains invalid characters."
        )

    return ValidatedInput(
        value=value,
        input_type="remote_target",
    )
