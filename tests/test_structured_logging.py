"""Tests for structured runtime logging."""

import logging

import pytest

from packaging.structured_logging import (
    LogEvent,
    create_log_event,
    emit_log_event,
)


def test_log_event_stores_structured_fields():
    event = create_log_event(
        level=logging.INFO,
        event="startup_complete",
        component="bootstrap",
        message="Application started.",
    )

    assert event.level == logging.INFO
    assert event.event == "startup_complete"
    assert event.component == "bootstrap"
    assert event.message == "Application started."


def test_log_event_requires_valid_level():
    with pytest.raises(TypeError):
        create_log_event(
            level="INFO",
            event="event",
            component="component",
            message="message",
        )


def test_log_event_requires_event():
    with pytest.raises(ValueError):
        create_log_event(
            level=logging.INFO,
            event="",
            component="component",
            message="message",
        )


def test_log_event_requires_component():
    with pytest.raises(ValueError):
        create_log_event(
            level=logging.INFO,
            event="event",
            component="",
            message="message",
        )


def test_log_event_requires_message():
    with pytest.raises(ValueError):
        create_log_event(
            level=logging.INFO,
            event="event",
            component="component",
            message="",
        )


def test_emit_log_event_writes_event_and_message(caplog):
    logger = logging.getLogger("windows_technician_test")

    with caplog.at_level(logging.INFO, logger=logger.name):
        event = create_log_event(
            level=logging.INFO,
            event="diagnostic_started",
            component="diagnostics",
            message="Diagnostic collection started.",
        )

        emit_log_event(logger, event)

    assert "diagnostic_started" in caplog.text
    assert "Diagnostic collection started." in caplog.text


def test_emit_log_event_exposes_structured_event(caplog):
    logger = logging.getLogger("windows_technician_structured_test")

    with caplog.at_level(logging.INFO, logger=logger.name):
        event = create_log_event(
            level=logging.INFO,
            event="case_created",
            component="case",
            message="Diagnostic case created.",
        )

        emit_log_event(logger, event)

    record = caplog.records[0]

    assert record.wt_event == "case_created"
    assert record.wt_component == "case"


def test_emit_log_event_requires_logger():
    event = LogEvent(
        level=logging.INFO,
        event="event",
        component="component",
        message="message",
    )

    with pytest.raises(TypeError):
        emit_log_event(
            "not a logger",
            event,
        )


def test_emit_log_event_requires_log_event(tmp_path):
    logger = logging.getLogger("windows_technician_invalid_event")

    with pytest.raises(TypeError):
        emit_log_event(
            logger,
            "not an event",
        )


def test_log_event_is_immutable():
    event = LogEvent(
        level=logging.INFO,
        event="event",
        component="component",
        message="message",
    )

    with pytest.raises(AttributeError):
        event.message = "changed"


def test_different_log_levels_are_supported(caplog):
    logger = logging.getLogger("windows_technician_levels")

    with caplog.at_level(logging.DEBUG, logger=logger.name):
        emit_log_event(
            logger,
            LogEvent(
                level=logging.WARNING,
                event="warning",
                component="runtime",
                message="Runtime warning.",
            ),
        )

    assert caplog.records[0].levelno == logging.WARNING
