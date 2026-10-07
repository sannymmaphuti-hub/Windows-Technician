"""Integration tests for configuration and environment architecture."""

from pathlib import Path

import pytest

from packaging.configuration_environment_architecture import (
    ConfigurationEnvironmentArchitecture,
    build_configuration_environment_architecture,
    configuration_environment_is_consistent,
    configuration_environment_is_safe,
)
from packaging.permission_context import PermissionContext
from packaging.windows_environment import WindowsEnvironment


def make_windows_environment():
    return WindowsEnvironment(
        operating_system="Windows",
        operating_system_version="10.0.26200",
        windows_build="11",
        architecture="AMD64",
        python_version="3.14.4",
        application_version="0.9.0",
    )


def make_permission_context():
    return PermissionContext(
        user_name="test-user",
        is_admin=False,
        is_elevated=False,
        can_write_program_files=False,
        can_write_system_directory=False,
    )


@pytest.fixture
def architecture(tmp_path):
    user_root = tmp_path / "user"
    system_root = tmp_path / "system"

    user_root.mkdir()
    system_root.mkdir()

    return build_configuration_environment_architecture(
        project_root=tmp_path,
        user_data_root=user_root,
        system_data_root=system_root,
        windows_environment=make_windows_environment(),
        permission_context=make_permission_context(),
    )


def test_architecture_type(architecture):
    assert isinstance(
        architecture,
        ConfigurationEnvironmentArchitecture,
    )


def test_windows_environment_is_integrated(architecture):
    assert (
        architecture.windows.application_version
        == "0.9.0"
    )


def test_permission_context_is_integrated(architecture):
    assert architecture.permissions.user_name == "test-user"


def test_filesystem_environment_is_integrated(architecture):
    assert (
        architecture.filesystem.project_root
        == architecture.filesystem.project_root
    )


def test_configuration_locations_are_integrated(architecture):
    assert (
        architecture.configuration_locations
        .user_configuration.name
        == "settings.json"
    )


def test_configuration_sources_are_integrated(architecture):
    assert architecture.configuration_sources.user == {}
    assert architecture.configuration_sources.system == {}


def test_safe_defaults_are_applied(architecture):
    configuration = architecture.effective_configuration

    assert (
        configuration["remediation"][
            "authorized_by_default"
        ]
        is False
    )

    assert (
        configuration["remote"]["enabled"]
        is False
    )

    assert (
        configuration["telemetry"]["enabled"]
        is False
    )


def test_safe_configuration_contract(architecture):
    assert configuration_environment_is_safe(
        architecture
    )


def test_configuration_environment_is_consistent(
    architecture,
):
    assert configuration_environment_is_consistent(
        architecture
    )


def test_configuration_can_override_safe_defaults(
    architecture,
):
    settings = (
        architecture.configuration_locations
        .user_configuration
    )

    settings.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.write_text(
        '{"interface":{"theme":"dark"}}',
        encoding="utf-8",
    )

    rebuilt = build_configuration_environment_architecture(
        project_root=architecture.filesystem.project_root,
        user_data_root=settings.parent.parent,
        system_data_root=(
            architecture.configuration_locations
            .system_configuration.parent.parent
        ),
        windows_environment=make_windows_environment(),
        permission_context=make_permission_context(),
    )

    assert (
        rebuilt.effective_configuration[
            "interface"
        ]["theme"]
        == "dark"
    )

    assert (
        rebuilt.effective_configuration[
            "remote"
        ]["enabled"]
        is False
    )


def test_system_configuration_is_overridden_by_user(
    architecture,
):
    system_file = (
        architecture.configuration_locations
        .system_configuration
    )

    system_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    system_file.write_text(
        '{"remote":{"enabled":true}}',
        encoding="utf-8",
    )

    user_file = (
        architecture.configuration_locations
        .user_configuration
    )

    user_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    user_file.write_text(
        '{"remote":{"enabled":false}}',
        encoding="utf-8",
    )

    rebuilt = build_configuration_environment_architecture(
        project_root=architecture.filesystem.project_root,
        user_data_root=user_file.parent.parent,
        system_data_root=system_file.parent.parent,
        windows_environment=make_windows_environment(),
        permission_context=make_permission_context(),
    )

    assert (
        rebuilt.effective_configuration[
            "remote"
        ]["enabled"]
        is False
    )


def test_invalid_architecture_type_is_rejected():
    with pytest.raises(TypeError):
        configuration_environment_is_safe(
            object()
        )


def test_invalid_consistency_type_is_rejected():
    with pytest.raises(TypeError):
        configuration_environment_is_consistent(
            object()
        )


def test_default_builder_uses_detection(monkeypatch, tmp_path):
    windows = make_windows_environment()
    permissions = make_permission_context()

    monkeypatch.setattr(
        "packaging.configuration_environment_architecture."
        "detect_windows_environment",
        lambda: windows,
    )

    monkeypatch.setattr(
        "packaging.configuration_environment_architecture."
        "detect_permission_context",
        lambda: permissions,
    )

    user_root = tmp_path / "user"
    system_root = tmp_path / "system"

    user_root.mkdir()
    system_root.mkdir()

    architecture = (
        build_configuration_environment_architecture(
            project_root=tmp_path,
            user_data_root=user_root,
            system_data_root=system_root,
        )
    )

    assert architecture.windows == windows
    assert architecture.permissions == permissions
