"""Tests for technician troubleshooting information."""

from datetime import datetime, timezone

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.error_context import create_error_context
from packaging.technician_troubleshooting import (
    TechnicianTroubleshootingRecord,
    build_troubleshooting_record,
    troubleshooting_record_to_dict,
)


def _context():
    return create_error_context(
        error=RuntimeError("diagnostic collection failed"),
        component="diagnostics",
        operation="collect_system_information",
        timestamp=datetime(
            2026,
            10,
            6,
            20,
            30,
            tzinfo=timezone.utc,
        ),
    )


def test_record_contains_application_identity():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.application_name == (
        APPLICATION_METADATA.display_name
    )
    assert record.application_version == (
        APPLICATION_METADATA.version
    )


def test_record_contains_component():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.component == "diagnostics"


def test_record_contains_operation():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.operation == (
        "collect_system_information"
    )


def test_record_contains_error_information():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.error_type == "RuntimeError"
    assert record.message == (
        "diagnostic collection failed"
    )


def test_record_contains_recovery_action():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.recovery_action == "degraded"


def test_record_contains_timestamp():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert record.timestamp.tzinfo is not None


def test_record_contains_human_readable_summary():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    assert "diagnostics failed" in record.summary
    assert "collect_system_information" in record.summary
    assert "diagnostic collection failed" in record.summary


def test_record_requires_context():
    with pytest.raises(TypeError):
        build_troubleshooting_record(
            context="invalid",
            recovery_action="degraded",
        )


def test_record_requires_recovery_action():
    with pytest.raises(ValueError):
        build_troubleshooting_record(
            context=_context(),
            recovery_action="",
        )


def test_record_can_be_serialized():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    result = troubleshooting_record_to_dict(record)

    assert result["application_name"] == (
        APPLICATION_METADATA.display_name
    )
    assert result["application_version"] == (
        APPLICATION_METADATA.version
    )
    assert result["error_type"] == "RuntimeError"
    assert result["recovery_action"] == "degraded"
    assert result["timestamp"] == (
        record.timestamp.isoformat()
    )


def test_serialization_requires_record():
    with pytest.raises(TypeError):
        troubleshooting_record_to_dict("invalid")


def test_record_is_immutable():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="degraded",
    )

    with pytest.raises(AttributeError):
        record.summary = "changed"


def test_record_matches_error_context():
    context = _context()

    record = build_troubleshooting_record(
        context=context,
        recovery_action="continue",
    )

    assert record.component == context.component
    assert record.operation == context.operation
    assert record.error_type == context.error_type
    assert record.message == context.message
    assert record.timestamp == context.timestamp


def test_record_has_expected_shape():
    record = build_troubleshooting_record(
        context=_context(),
        recovery_action="continue",
    )

    assert isinstance(
        record,
        TechnicianTroubleshootingRecord,
    )
    assert isinstance(record.summary, str)
