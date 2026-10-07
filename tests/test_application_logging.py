from pathlib import Path

import pytest

from engine.application_logging import (
    ApplicationLogger,
    CrashBoundary,
)


def test_logger_without_path_returns_formatted_entry():
    logger = ApplicationLogger()

    entry = logger.info("Application started")

    assert "| INFO |" in entry
    assert "Application started" in entry


def test_logger_writes_to_file(tmp_path):
    log_path = tmp_path / "logs" / "application.log"

    logger = ApplicationLogger(log_path)

    logger.info("Application started")

    assert log_path.exists()

    content = log_path.read_text(
        encoding="utf-8"
    )

    assert "INFO" in content
    assert "Application started" in content


def test_logger_creates_parent_directory(tmp_path):
    log_path = (
        tmp_path
        / "nested"
        / "logs"
        / "application.log"
    )

    logger = ApplicationLogger(log_path)

    logger.warning("Test warning")

    assert log_path.exists()


@pytest.mark.parametrize(
    "level",
    [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ],
)
def test_supported_levels(level):
    logger = ApplicationLogger()

    entry = logger.log(
        level,
        "test",
    )

    assert f"| {level} |" in entry


def test_level_is_normalized():
    logger = ApplicationLogger()

    entry = logger.log(
        " warning ",
        "test",
    )

    assert "| WARNING |" in entry


def test_invalid_level_is_rejected():
    logger = ApplicationLogger()

    with pytest.raises(ValueError):
        logger.log(
            "INVALID",
            "test",
        )


def test_non_string_level_is_rejected():
    logger = ApplicationLogger()

    with pytest.raises(ValueError):
        logger.log(
            123,
            "test",
        )


def test_empty_message_is_rejected():
    logger = ApplicationLogger()

    with pytest.raises(ValueError):
        logger.info("")


def test_non_string_message_is_rejected():
    logger = ApplicationLogger()

    with pytest.raises(ValueError):
        logger.info(123)


def test_convenience_methods_use_correct_levels():
    logger = ApplicationLogger()

    assert "| DEBUG |" in logger.debug("a")
    assert "| INFO |" in logger.info("b")
    assert "| WARNING |" in logger.warning("c")
    assert "| ERROR |" in logger.error("d")
    assert "| CRITICAL |" in logger.critical("e")


def test_multiple_entries_are_appended(tmp_path):
    log_path = tmp_path / "application.log"

    logger = ApplicationLogger(log_path)

    logger.info("first")
    logger.error("second")

    lines = log_path.read_text(
        encoding="utf-8"
    ).splitlines()

    assert len(lines) == 2
    assert "first" in lines[0]
    assert "second" in lines[1]


def test_crash_boundary_requires_exception():
    boundary = CrashBoundary()

    with pytest.raises(ValueError):
        boundary.handle("not an exception")


def test_crash_boundary_returns_error_record():
    boundary = CrashBoundary()

    result = boundary.handle(
        RuntimeError("startup failed")
    )

    assert result == {
        "status": "ERROR",
        "error_type": "RuntimeError",
        "message": "startup failed",
    }


def test_crash_boundary_logs_exception(tmp_path):
    log_path = tmp_path / "application.log"

    logger = ApplicationLogger(log_path)
    boundary = CrashBoundary(logger)

    boundary.handle(
        RuntimeError("startup failed")
    )

    content = log_path.read_text(
        encoding="utf-8"
    )

    assert "CRITICAL" in content
    assert "RuntimeError" in content
    assert "startup failed" in content


def test_protect_success():
    boundary = CrashBoundary()

    result = boundary.protect(
        lambda: 42
    )

    assert result == {
        "status": "SUCCESS",
        "result": 42,
    }


def test_protect_catches_exception():
    boundary = CrashBoundary()

    def failing_operation():
        raise RuntimeError("boom")

    result = boundary.protect(
        failing_operation
    )

    assert result == {
        "status": "ERROR",
        "error_type": "RuntimeError",
        "message": "boom",
    }


def test_protect_logs_exception(tmp_path):
    log_path = tmp_path / "application.log"

    logger = ApplicationLogger(log_path)
    boundary = CrashBoundary(logger)

    result = boundary.protect(
        lambda: 1 / 0
    )

    assert result["status"] == "ERROR"

    content = log_path.read_text(
        encoding="utf-8"
    )

    assert "CRITICAL" in content
    assert "ZeroDivisionError" in content


def test_successful_operation_is_not_logged_as_crash(
    tmp_path,
):
    log_path = tmp_path / "application.log"

    logger = ApplicationLogger(log_path)
    boundary = CrashBoundary(logger)

    boundary.protect(
        lambda: "ok"
    )

    if log_path.exists():
        content = log_path.read_text(
            encoding="utf-8"
        )
        assert "CRITICAL" not in content


def test_logging_has_no_diagnostic_surface():
    logger = ApplicationLogger()

    assert not hasattr(logger, "diagnose")
    assert not hasattr(logger, "analyze")
    assert not hasattr(logger, "remediate")
    assert not hasattr(logger, "execute")


def test_crash_boundary_has_no_remediation_surface():
    boundary = CrashBoundary()

    assert not hasattr(boundary, "remediate")
    assert not hasattr(boundary, "execute")
    assert not hasattr(boundary, "authorize")


def test_log_path_is_optional():
    logger = ApplicationLogger()

    assert logger.log_path is None


def test_log_path_is_path_object(tmp_path):
    log_path = tmp_path / "application.log"

    logger = ApplicationLogger(log_path)

    assert isinstance(
        logger.log_path,
        Path,
    )
