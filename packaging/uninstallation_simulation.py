"""Deterministic uninstallation simulation for Windows Technician."""

from dataclasses import dataclass
from pathlib import Path
import shutil

from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class UninstallationSimulationResult:
    success: bool
    installation_root: Path
    application_removed: bool
    configuration_preserved: bool
    logs_preserved: bool
    reports_preserved: bool
    shortcuts_removed: bool
    errors: tuple[str, ...] = ()


def _capture_files(root: Path | None) -> dict[Path, bytes]:
    if root is None or not root.exists():
        return {}

    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def _files_equal(
    root: Path | None,
    expected: dict[Path, bytes],
) -> bool:
    if root is None:
        return True

    return _capture_files(root) == expected


def simulate_uninstallation(
    *,
    installation_root: Path,
    configuration_root: Path | None = None,
    logs_root: Path | None = None,
    reports_root: Path | None = None,
    shortcuts_root: Path | None = None,
    remove_user_data: bool = False,
) -> UninstallationSimulationResult:
    """Simulate application-only uninstallation.

    By default, the application installation and shortcuts are removed.
    Configuration, logs, and reports remain untouched.

    User-data removal is an explicit operation and is never performed by
    the default uninstall path.
    """
    installation_root = Path(installation_root)

    preserved_roots = {
        "configuration": (
            Path(configuration_root)
            if configuration_root is not None
            else None
        ),
        "logs": Path(logs_root) if logs_root is not None else None,
        "reports": Path(reports_root) if reports_root is not None else None,
    }

    preserved = {
        name: _capture_files(root)
        for name, root in preserved_roots.items()
    }

    errors: list[str] = []

    # The installation root is an application-only boundary.
    if installation_root.exists():
        if not installation_root.is_dir():
            errors.append(
                "Installation root must be a directory."
            )
        else:
            shutil.rmtree(installation_root)

    # Remove application shortcuts separately.
    shortcuts_removed = True

    if shortcuts_root is not None:
        shortcuts_root = Path(shortcuts_root)

        if shortcuts_root.exists():
            if not shortcuts_root.is_dir():
                errors.append(
                    "Shortcuts root must be a directory."
                )
                shortcuts_removed = False
            else:
                shortcut_name = INSTALLER_CONTRACT.shortcut_name

                for path in shortcuts_root.rglob("*"):
                    if (
                        path.is_file()
                        and path.stem == shortcut_name
                    ):
                        path.unlink()

    # User data is deliberately preserved by default.
    #
    # An explicit user-data deletion operation can be added later behind
    # a dedicated confirmation boundary. It is not part of normal uninstall.
    if remove_user_data:
        errors.append(
            "User-data removal requires an explicit destructive operation."
        )

    application_removed = not installation_root.exists()

    configuration_preserved = _files_equal(
        preserved_roots["configuration"],
        preserved["configuration"],
    )

    logs_preserved = _files_equal(
        preserved_roots["logs"],
        preserved["logs"],
    )

    reports_preserved = _files_equal(
        preserved_roots["reports"],
        preserved["reports"],
    )

    if not application_removed:
        errors.append(
            "Application installation was not completely removed."
        )

    if not configuration_preserved:
        errors.append(
            "Configuration was modified during uninstall."
        )

    if not logs_preserved:
        errors.append(
            "Logs were modified during uninstall."
        )

    if not reports_preserved:
        errors.append(
            "Reports were modified during uninstall."
        )

    return UninstallationSimulationResult(
        success=not errors,
        installation_root=installation_root,
        application_removed=application_removed,
        configuration_preserved=configuration_preserved,
        logs_preserved=logs_preserved,
        reports_preserved=reports_preserved,
        shortcuts_removed=shortcuts_removed,
        errors=tuple(errors),
    )
