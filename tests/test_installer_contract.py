"""Tests for the Windows Technician installer contract."""

from pathlib import Path

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installer_contract import (
    INSTALLER_CONTRACT,
    installation_root,
    start_menu_directory,
)


def test_installer_matches_application_metadata():
    assert (
        INSTALLER_CONTRACT.application_name
        == APPLICATION_METADATA.display_name
    )
    assert INSTALLER_CONTRACT.version == APPLICATION_METADATA.version
    assert (
        INSTALLER_CONTRACT.executable_name
        == APPLICATION_METADATA.executable_name
    )


def test_installer_identity_is_v09():
    assert INSTALLER_CONTRACT.application_name == "Windows Technician"
    assert INSTALLER_CONTRACT.version.startswith("0.9.")
    assert INSTALLER_CONTRACT.executable_name == "WindowsTechnician.exe"


def test_installation_identity():
    assert INSTALLER_CONTRACT.install_directory_name == "Windows Technician"
    assert INSTALLER_CONTRACT.start_menu_directory_name == "Windows Technician"
    assert INSTALLER_CONTRACT.shortcut_name == "Windows Technician"


def test_upgrade_preserves_configuration():
    assert INSTALLER_CONTRACT.preserve_configuration_on_upgrade is True


def test_uninstall_preserves_configuration():
    assert INSTALLER_CONTRACT.preserve_configuration_on_uninstall is True


def test_installation_root_is_resolved_from_base_directory():
    base = Path("C:/Program Files")

    assert installation_root(base) == (
        base / "Windows Technician"
    )


def test_start_menu_directory_is_resolved_from_base_directory():
    base = Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs")

    assert start_menu_directory(base) == (
        base / "Windows Technician"
    )


def test_installation_root_requires_path():
    with pytest.raises(TypeError):
        installation_root("C:/Program Files")


def test_start_menu_directory_requires_path():
    with pytest.raises(TypeError):
        start_menu_directory("C:/ProgramData")


def test_installer_contract_is_immutable():
    with pytest.raises(AttributeError):
        INSTALLER_CONTRACT.version = "0.9.1"
