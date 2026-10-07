"""Production sensitive-information protection boundary."""

from dataclasses import dataclass
from enum import Enum
import re


class SensitiveDataType(str, Enum):
    PASSWORD = "PASSWORD"
    TOKEN = "TOKEN"
    API_KEY = "API_KEY"
    SECRET = "SECRET"
    CONNECTION_STRING = "CONNECTION_STRING"
    AUTHORIZATION_HEADER = "AUTHORIZATION_HEADER"
    PRIVATE_KEY = "PRIVATE_KEY"


@dataclass(frozen=True)
class RedactionResult:
    """Result of sanitizing potentially sensitive text."""

    value: str
    redacted: bool
    detected_types: tuple[SensitiveDataType, ...]

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise TypeError("value must be a string.")

        if not isinstance(self.redacted, bool):
            raise TypeError("redacted must be a boolean.")

        if not isinstance(self.detected_types, tuple):
            raise TypeError("detected_types must be a tuple.")

        if len(set(self.detected_types)) != len(self.detected_types):
            raise ValueError(
                "detected_types cannot contain duplicates."
            )

        for data_type in self.detected_types:
            if not isinstance(data_type, SensitiveDataType):
                raise TypeError(
                    "detected_types must contain SensitiveDataType values."
                )


_SECRET_PATTERNS = (
    (
        SensitiveDataType.PASSWORD,
        re.compile(
            r"(?i)(password|passwd|pwd)\s*[:=]\s*([^\s,;]+)"
        ),
    ),
    (
        SensitiveDataType.TOKEN,
        re.compile(
            r"(?i)(token)\s*[:=]\s*([^\s,;]+)"
        ),
    ),
    (
        SensitiveDataType.API_KEY,
        re.compile(
            r"(?i)(api[_-]?key)\s*[:=]\s*([^\s,;]+)"
        ),
    ),
    (
        SensitiveDataType.SECRET,
        re.compile(
            r"(?i)(secret)\s*[:=]\s*([^\s,;]+)"
        ),
    ),
    (
        SensitiveDataType.CONNECTION_STRING,
        re.compile(
            r"(?i)(connection[_ ]?string)\s*[:=]\s*([^\r\n]+)"
        ),
    ),
    (
        SensitiveDataType.AUTHORIZATION_HEADER,
        re.compile(
            r"(?i)(authorization)\s*:\s*(.+)"
        ),
    ),
    (
        SensitiveDataType.PRIVATE_KEY,
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?"
            r"-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
)


def redact_sensitive_information(
    value: str,
) -> RedactionResult:
    """Redact recognized sensitive values from text."""

    if not isinstance(value, str):
        raise TypeError("value must be a string.")

    sanitized = value
    detected: list[SensitiveDataType] = []

    for data_type, pattern in _SECRET_PATTERNS:
        if pattern.search(sanitized):
            detected.append(data_type)

            if data_type == SensitiveDataType.PRIVATE_KEY:
                sanitized = pattern.sub(
                    "[REDACTED PRIVATE KEY]",
                    sanitized,
                )
            else:
                sanitized = pattern.sub(
                    lambda match: (
                        f"{match.group(1)}=[REDACTED]"
                    ),
                    sanitized,
                )

    return RedactionResult(
        value=sanitized,
        redacted=sanitized != value,
        detected_types=tuple(detected),
    )


def contains_sensitive_information(
    value: str,
) -> bool:
    """Return whether recognized sensitive data exists in text."""

    return redact_sensitive_information(value).redacted


def sanitize_for_logging(
    value: str,
) -> str:
    """Return text safe for production logging."""

    return redact_sensitive_information(value).value
