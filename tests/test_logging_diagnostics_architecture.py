"""Tests for the logging and diagnostics integration lock."""

from pathlib import Path

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.logging_architecture import (
    build_logging_configuration,
)
from packaging.log_rotation import (
    DEFAULT_LOG_ROTATION_POLICY,
    LogRotationPolicy,
)
from packaging.logging_diagnostics_architecture import (
    LoggingDiagnosticsArchitecture,
    build_logging_diagnostics_architecture,
    build_technician_record,
    logging_diagnostics_architecture_is_consistent,
)
from packaging.technician_troubleshooting import (
    TechnicianTroubleshootingRecord,
)


def test_architecture_uses_application_identity(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert architecture.application_name == (
        APPLICATION_METADATA.display_name
    )

    assert architecture.application_version == (
        APPLICATION_METADATA.version
    )


def test_architecture_preserves_logging_configuration(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert architecture.logging is logging_configuration


def test_architecture_preserves_rotation_policy(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    policy = LogRotationPolicy(
        max_bytes=1234,
        backup_count=3,
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=policy,
    )

    assert architecture.rotation is policy


def test_architecture_requires_logging_configuration():
    with pytest.raises(TypeError):
        build_logging_diagnostics_architecture(
            logging_configuration="invalid",
            rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
        )


def test_architecture_requires_rotation_policy(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    with pytest.raises(TypeError):
        build_logging_diagnostics_architecture(
            logging_configuration=logging_configuration,
            rotation_policy="invalid",
        )


def test_architecture_is_consistent(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert logging_diagnostics_architecture_is_consistent(
        architecture
    )


def test_consistency_requires_architecture():
    with pytest.raises(TypeError):
        logging_diagnostics_architecture_is_consistent(
            "invalid"
        )


def test_architecture_is_frozen(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    with pytest.raises(AttributeError):
        architecture.application_name = "Changed"


def test_build_technician_record_delegates_to_canonical_record(
    tmp_path,
):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert architecture is not None

    from packaging.error_context import create_error_context

    context = create_error_context(
        error=RuntimeError("failure"),
        component="diagnostics",
        operation="collect",
    )

    record = build_technician_record(
        context,
        "degraded",
    )

    assert isinstance(
        record,
        TechnicianTroubleshootingRecord,
    )


def test_rotation_policy_remains_bounded(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert architecture.rotation.max_bytes > 0
    assert architecture.rotation.backup_count >= 0


def test_log_directory_is_a_path(tmp_path):
    logging_configuration = build_logging_configuration(
        tmp_path
    )

    architecture = build_logging_diagnostics_architecture(
        logging_configuration=logging_configuration,
        rotation_policy=DEFAULT_LOG_ROTATION_POLICY,
    )

    assert isinstance(
        architecture.logging.log_directory,
        Path,
    )
