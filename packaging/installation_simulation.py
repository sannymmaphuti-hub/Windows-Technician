"""Deterministic installation simulation for Windows Technician."""

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile
import shutil

from packaging.installer_contract import INSTALLER_CONTRACT
from packaging.installer_artifact import INSTALLER_ARTIFACT_CONTRACT


@dataclass(frozen=True)
class InstallationSimulationResult:
    success: bool
    installation_root: Path
    executable: Path | None
    files_installed: int
    configuration_preserved: bool
    logs_preserved: bool
    reports_preserved: bool
    errors: tuple[str, ...] = ()


def simulate_installation(
    artifact: Path,
    *,
    installation_root: Path,
    configuration_root: Path | None = None,
    logs_root: Path | None = None,
    reports_root: Path | None = None,
) -> InstallationSimulationResult:
    errors: list[str] = []

    artifact = Path(artifact)
    installation_root = Path(installation_root)

    if not artifact.exists():
        return InstallationSimulationResult(
            success=False,
            installation_root=installation_root,
            executable=None,
            files_installed=0,
            configuration_preserved=False,
            logs_preserved=False,
            reports_preserved=False,
            errors=("Installer artifact does not exist.",),
        )

    if not artifact.is_file():
        return InstallationSimulationResult(
            success=False,
            installation_root=installation_root,
            executable=None,
            files_installed=0,
            configuration_preserved=False,
            logs_preserved=False,
            reports_preserved=False,
            errors=("Installer artifact must be a file.",),
        )

    if artifact.suffix.lower() != ".zip":
        return InstallationSimulationResult(
            success=False,
            installation_root=installation_root,
            executable=None,
            files_installed=0,
            configuration_preserved=False,
            logs_preserved=False,
            reports_preserved=False,
            errors=("Installer artifact must be a ZIP archive.",),
        )

    installation_root.mkdir(parents=True, exist_ok=True)

    preserved = {
        "configuration": configuration_root,
        "logs": logs_root,
        "reports": reports_root,
    }

    preserved_content: dict[str, dict[Path, bytes]] = {}

    for name, root in preserved.items():
        if root is None:
            continue

        root = Path(root)
        if not root.exists():
            continue

        files: dict[Path, bytes] = {}
        for file in root.rglob("*"):
            if file.is_file():
                files[file.relative_to(root)] = file.read_bytes()

        preserved_content[name] = files

    archive_root = INSTALLER_ARTIFACT_CONTRACT.artifact_name

    with ZipFile(artifact, "r") as archive:
        names = archive.namelist()

        for name in names:
            parts = Path(name).parts

            if ".." in parts:
                errors.append(
                    f"Installer archive contains path traversal: {name}"
                )
                continue

            if not name.startswith(archive_root + "/"):
                errors.append(
                    f"Installer archive contains unexpected root: {name}"
                )

        if errors:
            return InstallationSimulationResult(
                success=False,
                installation_root=installation_root,
                executable=None,
                files_installed=0,
                configuration_preserved=False,
                logs_preserved=False,
                reports_preserved=False,
                errors=tuple(errors),
            )

        for name in names:
            if name.endswith("/"):
                continue

            relative = name[len(archive_root) + 1:]
            destination = installation_root / relative

            destination.parent.mkdir(parents=True, exist_ok=True)

            with archive.open(name) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)

    executable = (
        installation_root
        / INSTALLER_CONTRACT.executable_name
    )

    if not executable.exists() or not executable.is_file():
        errors.append("Installed executable does not exist.")

    installed_files = sum(
        1
        for path in installation_root.rglob("*")
        if path.is_file()
    )

    preservation_results: dict[str, bool] = {}

    for name, root in preserved.items():
        if root is None:
            preservation_results[name] = True
            continue

        root = Path(root)
        current: dict[Path, bytes] = {}

        if root.exists():
            for file in root.rglob("*"):
                if file.is_file():
                    current[file.relative_to(root)] = file.read_bytes()

        preservation_results[name] = (
            current == preserved_content.get(name, {})
        )

    return InstallationSimulationResult(
        success=not errors,
        installation_root=installation_root,
        executable=executable if executable.exists() else None,
        files_installed=installed_files,
        configuration_preserved=preservation_results["configuration"],
        logs_preserved=preservation_results["logs"],
        reports_preserved=preservation_results["reports"],
        errors=tuple(errors),
    )
