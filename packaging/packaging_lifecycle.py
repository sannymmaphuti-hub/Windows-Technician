"""End-to-end production packaging lifecycle."""

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_artifact import build_installer_artifact
from packaging.installer_archive_validation import validate_installer_archive
from packaging.installation_simulation import simulate_installation
from packaging.packaged_runtime_validation import validate_packaged_runtime
from packaging.uninstallation_simulation import simulate_uninstallation
from packaging.upgrade_simulation import simulate_upgrade


@dataclass(frozen=True)
class PackagingLifecycleResult:
    success: bool
    artifact_created: bool
    archive_valid: bool
    installation_successful: bool
    runtime_valid: bool
    upgrade_successful: bool
    upgraded_runtime_valid: bool
    uninstallation_successful: bool
    configuration_preserved: bool
    logs_preserved: bool
    reports_preserved: bool
    errors: tuple[str, ...] = ()


def run_packaging_lifecycle(
    *,
    workspace: Path,
) -> PackagingLifecycleResult:
    workspace = Path(workspace)
    errors: list[str] = []

    installation_root = workspace / "installed" / "Windows Technician"
    configuration_root = workspace / "user-data" / "configuration"
    logs_root = workspace / "user-data" / "logs"
    reports_root = workspace / "user-data" / "reports"
    shortcuts_root = workspace / "user-data" / "shortcuts"

    configuration_root.mkdir(parents=True, exist_ok=True)
    logs_root.mkdir(parents=True, exist_ok=True)
    reports_root.mkdir(parents=True, exist_ok=True)
    shortcuts_root.mkdir(parents=True, exist_ok=True)

    configuration_marker = configuration_root / "settings.json"
    logs_marker = logs_root / "application.log"
    reports_marker = reports_root / "diagnostic-report.json"

    configuration_marker.write_text(
        '{"remediation_authorization": false}',
        encoding="utf-8",
    )
    logs_marker.write_text(
        "existing application history",
        encoding="utf-8",
    )
    reports_marker.write_text(
        '{"existing": true}',
        encoding="utf-8",
    )

    # 1. Build installer artifact.
    artifact_result = build_installer_artifact()

    if not artifact_result.success or artifact_result.artifact is None:
        errors.extend(artifact_result.errors)
        return PackagingLifecycleResult(
            success=False,
            artifact_created=False,
            archive_valid=False,
            installation_successful=False,
            runtime_valid=False,
            upgrade_successful=False,
            upgraded_runtime_valid=False,
            uninstallation_successful=False,
            configuration_preserved=False,
            logs_preserved=False,
            reports_preserved=False,
            errors=tuple(errors),
        )

    artifact = artifact_result.artifact

    # 2. Validate archive.
    archive_validation = validate_installer_archive(artifact)

    if not archive_validation.valid:
        errors.extend(archive_validation.errors)

    # 3. Install.
    installation = simulate_installation(
        artifact,
        installation_root=installation_root,
        configuration_root=configuration_root,
        logs_root=logs_root,
        reports_root=reports_root,
    )

    if not installation.success:
        errors.extend(installation.errors)

    # 4. Validate installed runtime.
    runtime = validate_packaged_runtime()

    if not runtime.started or not runtime.survived_startup:
        errors.extend(runtime.errors)

    # 5. Upgrade.
    upgrade = simulate_upgrade(
        artifact,
        installation_root=installation_root,
        installed_version="0.8.0",
        configuration_root=configuration_root,
        logs_root=logs_root,
        reports_root=reports_root,
        shortcuts_root=shortcuts_root,
    )

    if not upgrade.success:
        errors.extend(upgrade.errors)

    # 6. Validate runtime after upgrade.
    upgraded_runtime = validate_packaged_runtime()

    if (
        not upgraded_runtime.started
        or not upgraded_runtime.survived_startup
    ):
        errors.extend(upgraded_runtime.errors)

    # 7. Uninstall.
    uninstall = simulate_uninstallation(
        installation_root=installation_root,
        configuration_root=configuration_root,
        logs_root=logs_root,
        reports_root=reports_root,
        shortcuts_root=shortcuts_root,
    )

    if not uninstall.success:
        errors.extend(uninstall.errors)

    # 8. Final user-data boundary.
    configuration_preserved = (
        uninstall.configuration_preserved
        and configuration_marker.exists()
        and configuration_marker.read_text(
            encoding="utf-8"
        ) == '{"remediation_authorization": false}'
    )

    logs_preserved = (
        uninstall.logs_preserved
        and logs_marker.exists()
        and logs_marker.read_text(
            encoding="utf-8"
        ) == "existing application history"
    )

    reports_preserved = (
        uninstall.reports_preserved
        and reports_marker.exists()
        and reports_marker.read_text(
            encoding="utf-8"
        ) == '{"existing": true}'
    )

    if not configuration_preserved:
        errors.append("Configuration was not preserved.")

    if not logs_preserved:
        errors.append("Logs were not preserved.")

    if not reports_preserved:
        errors.append("Reports were not preserved.")

    return PackagingLifecycleResult(
        success=not errors,
        artifact_created=True,
        archive_valid=archive_validation.valid,
        installation_successful=installation.success,
        runtime_valid=runtime.started and runtime.survived_startup,
        upgrade_successful=upgrade.success,
        upgraded_runtime_valid=(
            upgraded_runtime.started
            and upgraded_runtime.survived_startup
        ),
        uninstallation_successful=uninstall.success,
        configuration_preserved=configuration_preserved,
        logs_preserved=logs_preserved,
        reports_preserved=reports_preserved,
        errors=tuple(errors),
    )
