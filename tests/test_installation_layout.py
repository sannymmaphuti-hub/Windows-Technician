"""Tests for the Windows Technician installation layout."""

from pathlib import Path

import pytest

from packaging.installation_layout import (
    InstallationLayout,
    build_installation_layout,
    installation_contains_user_data,
)
from packaging.installer_contract import INSTALLER_CONTRACT


def test_installation_layout_uses_installer_identity():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.install_root == (
        Path("C:/Program Files")
        / INSTALLER_CONTRACT.install_directory_name
    )


def test_executable_is_inside_install_root():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.executable == (
        layout.install_root
        / INSTALLER_CONTRACT.executable_name
    )


def test_application_files_are_inside_install_root():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.application_files == (
        layout.install_root / "application"
    )


def test_resources_are_inside_install_root():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.resources == layout.install_root / "resources"


def test_user_logs_are_outside_install_root():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.logs == (
        Path("C:/Users/Test/AppData/Local/WindowsTechnician")
        / "logs"
    )

    assert not layout.logs.is_relative_to(layout.install_root)


def test_user_configuration_is_outside_install_root():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert layout.configuration == (
        Path("C:/Users/Test/AppData/Local/WindowsTechnician")
        / "config"
    )

    assert not layout.configuration.is_relative_to(
        layout.install_root
    )


def test_installation_does_not_contain_user_data():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert installation_contains_user_data(layout) is False


def test_layout_is_immutable():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    with pytest.raises(AttributeError):
        layout.install_root = Path("C:/Other")


def test_build_requires_paths():
    with pytest.raises(TypeError):
        build_installation_layout(
            "C:/Program Files",
            Path("C:/Users/Test"),
        )

    with pytest.raises(TypeError):
        build_installation_layout(
            Path("C:/Program Files"),
            "C:/Users/Test",
        )


def test_layout_type():
    layout = build_installation_layout(
        Path("C:/Program Files"),
        Path("C:/Users/Test/AppData/Local/WindowsTechnician"),
    )

    assert isinstance(layout, InstallationLayout)
