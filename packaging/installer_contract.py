"""Windows Technician installer contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.application_metadata import APPLICATION_METADATA


@dataclass(frozen=True)
class InstallerContract:
    application_name: str
    version: str
    executable_name: str
    install_directory_name: str
    start_menu_directory_name: str
    shortcut_name: str
    preserve_configuration_on_upgrade: bool
    preserve_configuration_on_uninstall: bool

    def __post_init__(self):
        values = {
            "application_name": self.application_name,
            "version": self.version,
            "executable_name": self.executable_name,
            "install_directory_name": self.install_directory_name,
            "start_menu_directory_name": self.start_menu_directory_name,
            "shortcut_name": self.shortcut_name,
        }

        for field_name, value in values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.version != APPLICATION_METADATA.version:
            raise ValueError(
                "Installer version must match application metadata."
            )


INSTALLER_CONTRACT = InstallerContract(
    application_name=APPLICATION_METADATA.display_name,
    version=APPLICATION_METADATA.version,
    executable_name=APPLICATION_METADATA.executable_name,
    install_directory_name="Windows Technician",
    start_menu_directory_name="Windows Technician",
    shortcut_name="Windows Technician",
    preserve_configuration_on_upgrade=True,
    preserve_configuration_on_uninstall=True,
)


def installation_root(base_directory: Path) -> Path:
    """Return the application installation directory."""
    if not isinstance(base_directory, Path):
        raise TypeError("base_directory must be a Path.")

    return base_directory / INSTALLER_CONTRACT.install_directory_name


def start_menu_directory(base_directory: Path) -> Path:
    """Return the Start Menu application directory."""
    if not isinstance(base_directory, Path):
        raise TypeError("base_directory must be a Path.")

    return base_directory / INSTALLER_CONTRACT.start_menu_directory_name
