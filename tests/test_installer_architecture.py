"""Integration tests for the complete installer architecture."""

from pathlib import Path

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.configuration_preservation import (
    CONFIGURATION_PRESERVATION_CONTRACT,
)
from packaging.installer_architecture import (
    INSTALLER_ARCHITECTURE,
    build_installer_layout,
    installer_architecture_is_consistent,
)
from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.shortcut_contract import SHORTCUT_CONTRACT
from packaging.uninstall_contract import UNINSTALL_CONTRACT
from packaging.upgrade_contract import UPGRADE_CONTRACT


def test_installer_architecture_matches_metadata():
    assert (
        INSTALLER_ARCHITECTURE.application_name
        == APPLICATION_METADATA.display_name
    )
    assert INSTALLER_ARCHITECTURE.version == APPLICATION_METADATA.version


def test_installer_architecture_matches_installer_contract():
    assert (
        INSTALLER_ARCHITECTURE.executable_name
        == INSTALLER_CONTRACT.executable_name
    )
    assert (
        INSTALLER_ARCHITECTURE.install_directory_name
        == INSTALLER_CONTRACT.install_directory_name
    )


def test_installer_architecture_matches_shortcut_contract():
    assert (
        INSTALLER_ARCHITECTURE.shortcut_name
        == SHORTCUT_CONTRACT.name
    )


def test_installer_architecture_matches_configuration_contract():
    assert (
        INSTALLER_ARCHITECTURE.configuration_filename
        == CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename
    )


def test_installer_architecture_preserves_configuration():
    assert INSTALLER_ARCHITECTURE.preserves_configuration is True


def test_installer_architecture_preserves_logs():
    assert INSTALLER_ARCHITECTURE.preserves_logs is True


def test_installer_architecture_preserves_reports():
    assert INSTALLER_ARCHITECTURE.preserves_reports is True


def test_installer_architecture_blocks_downgrade():
    assert INSTALLER_ARCHITECTURE.allows_downgrade is False


def test_installer_architecture_is_consistent():
    assert installer_architecture_is_consistent()


def test_installer_layout_is_constructible():
    layout = build_installer_layout(
        Path("C:/Program Files"),
        Path(
            "C:/Users/Test/AppData/Local/WindowsTechnician"
        ),
    )

    assert layout.install_root == (
        Path("C:/Program Files")
        / INSTALLER_CONTRACT.install_directory_name
    )


def test_application_files_and_user_data_are_separated():
    layout = build_installer_layout(
        Path("C:/Program Files"),
        Path(
            "C:/Users/Test/AppData/Local/WindowsTechnician"
        ),
    )

    assert not layout.configuration.is_relative_to(
        layout.install_root
    )
    assert not layout.logs.is_relative_to(
        layout.install_root
    )


def test_installer_architecture_is_immutable():
    with pytest.raises(AttributeError):
        INSTALLER_ARCHITECTURE.version = "0.10.0"
