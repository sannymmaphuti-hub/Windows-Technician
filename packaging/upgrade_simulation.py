"""Deterministic upgrade simulation for Windows Technician."""

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
import shutil

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installer_artifact import INSTALLER_ARTIFACT_CONTRACT
from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class UpgradeSimulationResult:
    success: bool
    installation_root: Path
    executable: Path | None
    files_installed: int
    configuration_preserved: bool
    logs_preserved: bool
    reports_preserved: bool
    shortcuts_preserved: bool
    errors: tuple[str, ...] = ()


def _version_tuple(version: str) -> tuple[int, ...]:
    if not isinstance(version, str) or not version.strip():
        raise ValueError("Version must be a non-empty string.")

    try:
        values = tuple(int(part) for part in version.split("."))
    except ValueError as exc:
        raise ValueError(
            "Version must contain numeric components."
        ) from exc

    if not values:
        raise ValueError("Version must not be empty.")

    return values


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


def _failure(
    *,
    installation_root: Path,
    errors: list[str],
) -> UpgradeSimulationResult:
    return UpgradeSimulationResult(
        success=False,
        installation_root=installation_root,
        executable=None,
        files_installed=0,
        configuration_preserved=False,
        logs_preserved=False,
        reports_preserved=False,
        shortcuts_preserved=False,
        errors=tuple(errors),
    )


def simulate_upgrade(
    artifact: Path,
    *,
    installation_root: Path,
    installed_version: str,
    configuration_root: Path | None = None,
    logs_root: Path | None = None,
    reports_root: Path | None = None,
    shortcuts_root: Path | None = None,
) -> UpgradeSimulationResult:
    """Simulate replacing an installed application with a newer package.

    The application installation root is replaced completely.

    Configuration, logs, reports, and shortcuts are deliberately treated
    as separate persistent data boundaries and are preserved.
    """
    artifact = Path(artifact)
    installation_root = Path(installation_root)

    errors: list[str] = []

    if _version_tuple(APPLICATION_METADATA.version) <= _version_tuple(
        installed_version
    ):
        errors.append(
            "Upgrade version must be newer than the installed version."
        )

    if not artifact.exists():
        errors.append("Upgrade artifact does not exist.")
    elif not artifact.is_file():
        errors.append("Upgrade artifact must be a file.")
    elif artifact.suffix.lower() != ".zip":
        errors.append("Upgrade artifact must be a ZIP archive.")

    if errors:
        return _failure(
            installation_root=installation_root,
            errors=errors,
        )

    preserved_roots = {
        "configuration": (
            Path(configuration_root)
            if configuration_root is not None
            else None
        ),
        "logs": Path(logs_root) if logs_root is not None else None,
        "reports": Path(reports_root) if reports_root is not None else None,
        "shortcuts": (
            Path(shortcuts_root)
            if shortcuts_root is not None
            else None
        ),
    }

    preserved = {
        name: _capture_files(root)
        for name, root in preserved_roots.items()
    }

    archive_root = INSTALLER_ARTIFACT_CONTRACT.artifact_name

    # Validate the archive before touching the existing installation.
    with ZipFile(artifact, "r") as archive:
        names = archive.namelist()

        for name in names:
            parts = Path(name).parts

            if ".." in parts:
                errors.append(
                    f"Upgrade archive contains path traversal: {name}"
                )
                continue

            if not name.startswith(archive_root + "/"):
                errors.append(
                    f"Upgrade archive contains unexpected root: {name}"
                )

    if errors:
        return _failure(
            installation_root=installation_root,
            errors=errors,
        )

    # The application installation is replaceable.
    #
    # Persistent user data is NOT located here and is therefore untouched.
    if installation_root.exists():
        if not installation_root.is_dir():
            return _failure(
                installation_root=installation_root,
                errors=["Installation root must be a directory."],
            )

        shutil.rmtree(installation_root)

    installation_root.mkdir(parents=True, exist_ok=True)

    # Install the new application payload.
    with ZipFile(artifact, "r") as archive:
        for name in archive.namelist():
            if name.endswith("/"):
                continue

            relative = name[len(archive_root) + 1:]
            destination = installation_root / relative

            destination.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with archive.open(name) as source:
                with destination.open("wb") as target:
                    shutil.copyfileobj(source, target)

    executable = (
        installation_root
        / INSTALLER_CONTRACT.executable_name
    )

    if not executable.exists() or not executable.is_file():
        errors.append("Upgraded executable does not exist.")

    installed_files = sum(
        1
        for path in installation_root.rglob("*")
        if path.is_file()
    )

    preservation = {
        name: _files_equal(root, preserved[name])
        for name, root in preserved_roots.items()
    }

    return UpgradeSimulationResult(
        success=not errors,
        installation_root=installation_root,
        executable=executable if executable.exists() else None,
        files_installed=installed_files,
        configuration_preserved=preservation["configuration"],
        logs_preserved=preservation["logs"],
        reports_preserved=preservation["reports"],
        shortcuts_preserved=preservation["shortcuts"],
        errors=tuple(errors),
    )
