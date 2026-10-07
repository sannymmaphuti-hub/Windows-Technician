"""Technician troubleshooting information boundary."""

from dataclasses import dataclass
from datetime import datetime

from packaging.application_metadata import APPLICATION_METADATA
from packaging.error_context import ErrorContext


@dataclass(frozen=True)
class TechnicianTroubleshootingRecord:
    application_name: str
    application_version: str
    component: str
    operation: str
    error_type: str
    message: str
    recovery_action: str
    timestamp: datetime
    summary: str

    def __post_init__(self):
        for field_name, value in (
            ("application_name", self.application_name),
            ("application_version", self.application_version),
            ("component", self.component),
            ("operation", self.operation),
            ("error_type", self.error_type),
            ("message", self.message),
            ("recovery_action", self.recovery_action),
            ("summary", self.summary),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(self.timestamp, datetime):
            raise TypeError(
                "timestamp must be a datetime."
            )


def build_troubleshooting_record(
    *,
    context: ErrorContext,
    recovery_action: str,
) -> TechnicianTroubleshootingRecord:
    if not isinstance(context, ErrorContext):
        raise TypeError(
            "context must be an ErrorContext."
        )

    if (
        not isinstance(recovery_action, str)
        or not recovery_action.strip()
    ):
        raise ValueError(
            "recovery_action must be a non-empty string."
        )

    summary = (
        f"{context.component} failed while performing "
        f"{context.operation}: {context.message}"
    )

    return TechnicianTroubleshootingRecord(
        application_name=APPLICATION_METADATA.display_name,
        application_version=APPLICATION_METADATA.version,
        component=context.component,
        operation=context.operation,
        error_type=context.error_type,
        message=context.message,
        recovery_action=recovery_action,
        timestamp=context.timestamp,
        summary=summary,
    )


def troubleshooting_record_to_dict(
    record: TechnicianTroubleshootingRecord,
) -> dict[str, str]:
    if not isinstance(
        record,
        TechnicianTroubleshootingRecord,
    ):
        raise TypeError(
            "record must be a TechnicianTroubleshootingRecord."
        )

    return {
        "application_name": record.application_name,
        "application_version": record.application_version,
        "component": record.component,
        "operation": record.operation,
        "error_type": record.error_type,
        "message": record.message,
        "recovery_action": record.recovery_action,
        "timestamp": record.timestamp.isoformat(),
        "summary": record.summary,
    }
