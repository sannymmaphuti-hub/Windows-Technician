"""Tests for log rotation and retention."""

import logging
from logging.handlers import RotatingFileHandler

import pytest

from packaging.log_rotation import (
    DEFAULT_LOG_ROTATION_POLICY,
    LogRotationPolicy,
    configure_rotating_file_logging,
    create_rotating_file_handler,
)


def test_default_rotation_policy_has_bounded_size():
    assert DEFAULT_LOG_ROTATION_POLICY.max_bytes > 0


def test_default_rotation_policy_has_bounded_backups():
    assert DEFAULT_LOG_ROTATION_POLICY.backup_count >= 0


def test_rotation_policy_requires_integer_max_bytes():
    with pytest.raises(TypeError):
        LogRotationPolicy(
            max_bytes="500",
            backup_count=5,
        )


def test_rotation_policy_requires_positive_max_bytes():
    with pytest.raises(ValueError):
        LogRotationPolicy(
            max_bytes=0,
            backup_count=5,
        )


def test_rotation_policy_requires_integer_backup_count():
    with pytest.raises(TypeError):
        LogRotationPolicy(
            max_bytes=500,
            backup_count="5",
        )


def test_rotation_policy_rejects_negative_backup_count():
    with pytest.raises(ValueError):
        LogRotationPolicy(
            max_bytes=500,
            backup_count=-1,
        )


def test_create_handler_requires_path():
    with pytest.raises(TypeError):
        create_rotating_file_handler(
            "logs/app.log"
        )


def test_create_handler_requires_policy():
    with pytest.raises(TypeError):
        create_rotating_file_handler(
            __import__("pathlib").Path("app.log"),
            policy="invalid",
        )


def test_create_handler_creates_parent_directory(tmp_path):
    path = tmp_path / "logs" / "app.log"

    handler = create_rotating_file_handler(path)

    try:
        assert path.parent.exists()
        assert path.parent.is_dir()
    finally:
        handler.close()


def test_create_handler_returns_rotating_handler(tmp_path):
    path = tmp_path / "app.log"

    handler = create_rotating_file_handler(path)

    try:
        assert isinstance(
            handler,
            RotatingFileHandler,
        )
    finally:
        handler.close()


def test_handler_uses_requested_rotation_policy(tmp_path):
    path = tmp_path / "app.log"

    policy = LogRotationPolicy(
        max_bytes=1234,
        backup_count=7,
    )

    handler = create_rotating_file_handler(
        path,
        policy,
    )

    try:
        assert handler.maxBytes == 1234
        assert handler.backupCount == 7
    finally:
        handler.close()


def test_configure_logging_adds_handler(tmp_path):
    logger = logging.getLogger(
        "windows_technician_rotation_test"
    )
    logger.handlers.clear()

    handler = configure_rotating_file_logging(
        logger,
        tmp_path / "app.log",
    )

    try:
        assert handler in logger.handlers
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_configure_logging_sets_formatter(tmp_path):
    logger = logging.getLogger(
        "windows_technician_formatter_test"
    )
    logger.handlers.clear()

    handler = configure_rotating_file_logging(
        logger,
        tmp_path / "app.log",
    )

    try:
        assert handler.formatter is not None
        assert "%(asctime)s" in handler.formatter._fmt
        assert "%(levelname)s" in handler.formatter._fmt
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_log_file_receives_runtime_message(tmp_path):
    path = tmp_path / "app.log"

    logger = logging.getLogger(
        "windows_technician_file_test"
    )
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    handler = configure_rotating_file_logging(
        logger,
        path,
    )

    try:
        logger.info("runtime event")
        handler.flush()

        content = path.read_text(
            encoding="utf-8"
        )

        assert "runtime event" in content
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_rotation_occurs_when_size_limit_is_reached(tmp_path):
    path = tmp_path / "app.log"

    logger = logging.getLogger(
        "windows_technician_rotation_behavior_test"
    )
    logger.handlers.clear()
    logger.setLevel(logging.INFO)

    policy = LogRotationPolicy(
        max_bytes=100,
        backup_count=2,
    )

    handler = configure_rotating_file_logging(
        logger,
        path,
        policy,
    )

    try:
        for index in range(20):
            logger.info(
                "large runtime message %s %s",
                index,
                "x" * 30,
            )

        handler.flush()

        rotated_files = list(
            tmp_path.glob("app.log.*")
        )

        assert rotated_files
        assert len(rotated_files) <= 2
    finally:
        logger.removeHandler(handler)
        handler.close()


def test_rotation_policy_is_immutable():
    policy = LogRotationPolicy(
        max_bytes=100,
        backup_count=2,
    )

    with pytest.raises(AttributeError):
        policy.max_bytes = 200
