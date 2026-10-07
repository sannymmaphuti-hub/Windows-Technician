"""Integrated Windows Technician installer architecture."""

from dataclasses import dataclass
from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA
from packaging.configuration_preservation import (
    CONFIGURATION_PRESERVATION_CONTRACT,
)
from packaging.installation_layout import (
    InstallationLayout,
    build_installation_layout,
)
from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.shortcut_contract import SHORTCUT_CONTRACT
from packaging.uninstall_contract import UNINSTALL_CONTRACT
from packaging.upgrade_contract import UPGRADE_CONTRACT


@dataclass(frozen=True)
class InstallerArchitecture:
    application_name: str
    version: str
    executable_name: str
    install_directory_name: str
    shortcut_name: str
    configuration_filename: str
    preserves_configuration: bool
    preserves_logs: bool
    preserves_reports: bool
    allows_downgrade: bool


INSTALLER_ARCHITECTURE = InstallerArchitecture(
    application_name=APPLICATION_METADATA.display_name,
    version=APPLICATION_METADATA.version,
    executable_name=APPLICATION_METADATA.executable_name,
    install_directory_name=INSTALLER_CONTRACT.install_directory_name,
    shortcut_name=SHORTCUT_CONTRACT.name,
    configuration_filename=(
        CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename
    ),
    preserves_configuration=(
        UNINSTALL_CONTRACT.preserve_configuration
        and UPGRADE_CONTRACT.preserve_configuration
    ),
    preserves_logs=(
        UNINSTALL_CONTRACT.preserve_logs
        and UPGRADE_CONTRACT.preserve_logs
    ),
    preserves_reports=(
        UNINSTALL_CONTRACT.preserve_reports
        and UPGRADE_CONTRACT.preserve_reports
    ),
    allows_downgrade=UPGRADE_CONTRACT.allow_downgrade,
)


def build_installer_layout(
    install_base: Path,
    user_data_root: Path,
) -> InstallationLayout:
    return build_installation_layout(
        install_base,
        user_data_root,
    )


def installer_architecture_is_consistent() -> bool:
    return (
        INSTALLER_ARCHITECTURE.application_name
        == APPLICATION_METADATA.display_name
        and INSTALLER_ARCHITECTURE.version
        == APPLICATION_METADATA.version
        and INSTALLER_ARCHITECTURE.executable_name
        == INSTALLER_CONTRACT.executable_name
        and INSTALLER_ARCHITECTURE.install_directory_name
        == INSTALLER_CONTRACT.install_directory_name
        and INSTALLER_ARCHITECTURE.shortcut_name
        == SHORTCUT_CONTRACT.name
        and INSTALLER_ARCHITECTURE.configuration_filename
        == CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename
        and INSTALLER_ARCHITECTURE.preserves_configuration
        and INSTALLER_ARCHITECTURE.preserves_logs
        and INSTALLER_ARCHITECTURE.preserves_reports
        and not INSTALLER_ARCHITECTURE.allows_downgrade
    )
