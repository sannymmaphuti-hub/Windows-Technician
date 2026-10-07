"""Integrated logging and diagnostics architecture."""

from dataclasses import dataclass

from packaging.application_metadata import APPLICATION_METADATA
from packaging.error_context import ErrorContext
from packaging.logging_architecture import LoggingConfiguration
from packaging.log_rotation import LogRotationPolicy
from packaging.technician_troubleshooting import (
    TechnicianTroubleshootingRecord,
    build_troubleshooting_record,
)


@dataclass(frozen=True)
class LoggingDiagnosticsArchitecture:
    application_name: str
    application_version: str
    logging: LoggingConfiguration
    rotation: LogRotationPolicy


def build_logging_diagnostics_architecture(
    *,
    logging_configuration: LoggingConfiguration,
    rotation_policy: LogRotationPolicy,
) -> LoggingDiagnosticsArchitecture:
    if not isinstance(
        logging_configuration,
        LoggingConfiguration,
    ):
        raise TypeError(
            "logging_configuration must be a LoggingConfiguration."
        )

    if not isinstance(
        rotation_policy,
        LogRotationPolicy,
    ):
        raise TypeError(
            "rotation_policy must be a LogRotationPolicy."
        )

    return LoggingDiagnosticsArchitecture(
        application_name=APPLICATION_METADATA.display_name,
        application_version=APPLICATION_METADATA.version,
        logging=logging_configuration,
        rotation=rotation_policy,
    )


def build_technician_record(
    context: ErrorContext,
    recovery_action: str,
) -> TechnicianTroubleshootingRecord:
    return build_troubleshooting_record(
        context=context,
        recovery_action=recovery_action,
    )


def logging_diagnostics_architecture_is_consistent(
    architecture: LoggingDiagnosticsArchitecture,
) -> bool:
    if not isinstance(
        architecture,
        LoggingDiagnosticsArchitecture,
    ):
        raise TypeError(
            "architecture must be a LoggingDiagnosticsArchitecture."
        )

    return (
        architecture.application_name
        == APPLICATION_METADATA.display_name
        and architecture.application_version
        == APPLICATION_METADATA.version
        and architecture.logging.log_directory
        is not None
        and architecture.logging.log_filename.strip() != ""
        and architecture.rotation.max_bytes > 0
        and architecture.rotation.backup_count >= 0
    )
