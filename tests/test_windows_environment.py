"""Tests for the Windows environment compatibility boundary."""

from unittest.mock import patch

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.windows_environment import (
    WindowsEnvironment,
    detect_windows_environment,
    environment_is_supported,
)


def test_environment_contains_application_version():
    environment = detect_windows_environment()

    assert environment.application_version == (
        APPLICATION_METADATA.version
    )


def test_environment_contains_operating_system():
    environment = detect_windows_environment()

    assert isinstance(
        environment.operating_system,
        str,
    )
    assert environment.operating_system


def test_environment_contains_operating_system_version():
    environment = detect_windows_environment()

    assert isinstance(
        environment.operating_system_version,
        str,
    )
    assert environment.operating_system_version


def test_environment_contains_windows_build():
    environment = detect_windows_environment()

    assert isinstance(
        environment.windows_build,
        str,
    )
    assert environment.windows_build


def test_environment_contains_architecture():
    environment = detect_windows_environment()

    assert isinstance(
        environment.architecture,
        str,
    )
    assert environment.architecture


def test_environment_contains_python_version():
    environment = detect_windows_environment()

    assert isinstance(
        environment.python_version,
        str,
    )
    assert environment.python_version


def test_windows_environment_identifies_windows():
    environment = WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0",
        windows_build="11",
        architecture="AMD64",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert environment.is_windows


def test_non_windows_environment_is_not_windows():
    environment = WindowsEnvironment(
        operating_system="Linux",
        operating_system_version="6.0",
        windows_build="",
        architecture="x86_64",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert not environment.is_windows


def test_supported_windows_architecture_is_supported():
    environment = WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0",
        windows_build="26200",
        architecture="AMD64",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert environment.supports_application


def test_arm64_windows_is_supported():
    environment = WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0",
        windows_build="26200",
        architecture="ARM64",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert environment.supports_application


def test_x86_windows_is_supported():
    environment = WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0",
        windows_build="19045",
        architecture="x86",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert environment.supports_application


def test_non_windows_environment_is_not_supported():
    environment = WindowsEnvironment(
        operating_system="Linux",
        operating_system_version="6.0",
        windows_build="",
        architecture="x86_64",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert not environment.supports_application


def test_unsupported_architecture_is_not_supported():
    environment = WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0",
        windows_build="26200",
        architecture="MIPS",
        python_version="3.14.4",
        application_version=APPLICATION_METADATA.version,
    )

    assert not environment.supports_application


def test_environment_support_check_requires_environment():
    with pytest.raises(TypeError):
        environment_is_supported("invalid")


def test_environment_detection_uses_platform_information():
    with patch(
        "packaging.windows_environment.platform.system",
        return_value="Windows",
    ), patch(
        "packaging.windows_environment.platform.version",
        return_value="10.0.26200",
    ), patch(
        "packaging.windows_environment.platform.release",
        return_value="11",
    ), patch(
        "packaging.windows_environment.platform.machine",
        return_value="AMD64",
    ), patch(
        "packaging.windows_environment.platform.python_version",
        return_value="3.14.4",
    ):
        environment = detect_windows_environment()

    assert environment.operating_system == "Windows"
    assert environment.operating_system_version == "10.0.26200"
    assert environment.windows_build == "11"
    assert environment.architecture == "AMD64"
    assert environment.python_version == "3.14.4"


def test_environment_is_immutable():
    environment = detect_windows_environment()

    with pytest.raises(AttributeError):
        environment.architecture = "ARM64"
