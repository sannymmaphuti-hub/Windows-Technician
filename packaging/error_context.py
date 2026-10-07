"""Production error context and diagnostic records."""

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ErrorContext:
    error_type: str
    message: str
    component: str
    operation: str
    timestamp: datetime

    def __post_init__(self):
        for field_name, value in (
            ("error_type", self.error_type),
            ("message", self.message),
            ("component", self.component),
            ("operation", self.operation),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(self.timestamp, datetime):
            raise TypeError(
                "timestamp must be a datetime."
            )

        if self.timestamp.tzinfo is None:
            raise ValueError(
                "timestamp must be timezone-aware."
            )


def create_error_context(
    *,
    error: Exception,
    component: str,
    operation: str,
    timestamp: datetime | None = None,
) -> ErrorContext:
    if not isinstance(error, Exception):
        raise TypeError(
            "error must be an Exception."
        )

    if not isinstance(component, str) or not component.strip():
        raise ValueError(
            "component must be a non-empty string."
        )

    if not isinstance(operation, str) or not operation.strip():
        raise ValueError(
            "operation must be a non-empty string."
        )

    event_time = timestamp or datetime.now(
        timezone.utc
    )

    return ErrorContext(
        error_type=type(error).__name__,
        message=str(error) or "Operation failed.",
        component=component,
        operation=operation,
        timestamp=event_time,
    )


def error_context_to_dict(
    context: ErrorContext,
) -> dict[str, str]:
    if not isinstance(context, ErrorContext):
        raise TypeError(
            "context must be an ErrorContext."
        )

    return {
        "error_type": context.error_type,
        "message": context.message,
        "component": context.component,
        "operation": context.operation,
        "timestamp": context.timestamp.isoformat(),
    }
