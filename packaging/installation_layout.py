"""Windows Technician installation layout."""

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class InstallationLayout:
    install_root: Path
    executable: Path
    application_files: Path
    resources: Path
    logs: Path
    configuration: Path


def build_installation_layout(
    install_base: Path,
    user_data_root: Path,
) -> InstallationLayout:
    if not isinstance(install_base, Path):
        raise TypeError("install_base must be a Path.")

    if not isinstance(user_data_root, Path):
        raise TypeError("user_data_root must be a Path.")

    install_root = (
        install_base / INSTALLER_CONTRACT.install_directory_name
    )

    return InstallationLayout(
        install_root=install_root,
        executable=(
            install_root / INSTALLER_CONTRACT.executable_name
        ),
        application_files=install_root / "application",
        resources=install_root / "resources",
        logs=user_data_root / "logs",
        configuration=user_data_root / "config",
    )


def installation_contains_user_data(
    layout: InstallationLayout,
) -> bool:
    try:
        layout.logs.resolve().relative_to(
            layout.install_root.resolve()
        )
        return True
    except ValueError:
        pass

    try:
        layout.configuration.resolve().relative_to(
            layout.install_root.resolve()
        )
        return True
    except ValueError:
        return False
