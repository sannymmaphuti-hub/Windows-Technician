"""Windows Technician configuration preservation contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class ConfigurationPreservationContract:
    preserve_on_upgrade: bool
    preserve_on_uninstall: bool
    configuration_directory_name: str
    configuration_filename: str

    def __post_init__(self):
        if not self.configuration_directory_name.strip():
            raise ValueError(
                "configuration_directory_name must be non-empty."
            )

        if not self.configuration_filename.strip():
            raise ValueError(
                "configuration_filename must be non-empty."
            )


CONFIGURATION_PRESERVATION_CONTRACT = (
    ConfigurationPreservationContract(
        preserve_on_upgrade=(
            INSTALLER_CONTRACT.preserve_configuration_on_upgrade
        ),
        preserve_on_uninstall=(
            INSTALLER_CONTRACT.preserve_configuration_on_uninstall
        ),
        configuration_directory_name="config",
        configuration_filename="settings.json",
    )
)


def configuration_path(user_data_root: Path) -> Path:
    if not isinstance(user_data_root, Path):
        raise TypeError("user_data_root must be a Path.")

    return (
        user_data_root
        / CONFIGURATION_PRESERVATION_CONTRACT.configuration_directory_name
        / CONFIGURATION_PRESERVATION_CONTRACT.configuration_filename
    )


def configuration_is_outside_installation(
    configuration: Path,
    install_root: Path,
) -> bool:
    if not isinstance(configuration, Path):
        raise TypeError("configuration must be a Path.")

    if not isinstance(install_root, Path):
        raise TypeError("install_root must be a Path.")

    try:
        configuration.resolve().relative_to(
            install_root.resolve()
        )
        return False
    except ValueError:
        return True
