"""Tests for production logging architecture."""

import logging

import pytest

from packaging.logging_architecture import (
    LoggingConfiguration,
    build_logging_configuration,
    configure_logger,
)


def test_logging_configuration_has_canonical_logger_name(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    assert configuration.logger_name == (
        "windows_technician"
    )


def test_logging_configuration_has_production_filename(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    assert configuration.log_filename == (
        "windows-technician.log"
    )


def test_logging_configuration_uses_info_level(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    assert configuration.level == logging.INFO


def test_logging_configuration_requires_directory():
    with pytest.raises(TypeError):
        build_logging_configuration("logs")


def test_logging_configuration_requires_logger_name(tmp_path):
    with pytest.raises(ValueError):
        LoggingConfiguration(
            logger_name="",
            log_directory=tmp_path,
            log_filename="app.log",
            level=logging.INFO,
        )


def test_logging_configuration_requires_filename(tmp_path):
    with pytest.raises(ValueError):
        LoggingConfiguration(
            logger_name="windows_technician",
            log_directory=tmp_path,
            log_filename="",
            level=logging.INFO,
        )


def test_logging_configuration_requires_path(tmp_path):
    with pytest.raises(TypeError):
        LoggingConfiguration(
            logger_name="windows_technician",
            log_directory="logs",
            log_filename="app.log",
            level=logging.INFO,
        )


def test_logger_configuration_creates_directory(tmp_path):
    log_directory = tmp_path / "logs"

    configuration = build_logging_configuration(
        log_directory
    )

    configure_logger(configuration)

    assert log_directory.exists()
    assert log_directory.is_dir()


def test_configure_logger_returns_logger(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    logger = configure_logger(configuration)

    assert isinstance(logger, logging.Logger)
    assert logger.name == "windows_technician"


def test_configure_logger_sets_level(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    logger = configure_logger(configuration)

    assert logger.level == logging.INFO


def test_logging_configuration_is_immutable(tmp_path):
    configuration = build_logging_configuration(tmp_path)

    with pytest.raises(AttributeError):
        configuration.level = logging.DEBUG


def test_configure_logger_requires_configuration():
    with pytest.raises(TypeError):
        configure_logger(None)
