"""Windows Technician Windows-shell shortcut contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class ShortcutContract:
    name: str
    target_name: str
    start_menu_name: str
    desktop_name: str
    working_directory_name: str

    def __post_init__(self):
        values = {
            "name": self.name,
            "target_name": self.target_name,
            "start_menu_name": self.start_menu_name,
            "desktop_name": self.desktop_name,
            "working_directory_name": self.working_directory_name,
        }

        for field_name, value in values.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )


SHORTCUT_CONTRACT = ShortcutContract(
    name=INSTALLER_CONTRACT.shortcut_name,
    target_name=INSTALLER_CONTRACT.executable_name,
    start_menu_name=INSTALLER_CONTRACT.start_menu_directory_name,
    desktop_name=INSTALLER_CONTRACT.shortcut_name,
    working_directory_name=INSTALLER_CONTRACT.install_directory_name,
)


def shortcut_target(install_root: Path) -> Path:
    if not isinstance(install_root, Path):
        raise TypeError("install_root must be a Path.")

    return install_root / SHORTCUT_CONTRACT.target_name


def shortcut_working_directory(install_root: Path) -> Path:
    if not isinstance(install_root, Path):
        raise TypeError("install_root must be a Path.")

    return install_root


def shortcut_is_installation_bound(
    install_root: Path,
    target: Path,
) -> bool:
    if not isinstance(install_root, Path):
        raise TypeError("install_root must be a Path.")

    if not isinstance(target, Path):
        raise TypeError("target must be a Path.")

    try:
        target.resolve().relative_to(install_root.resolve())
        return True
    except ValueError:
        return False
