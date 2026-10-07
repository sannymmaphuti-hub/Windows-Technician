"""Tests for deterministic upgrade simulation."""

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installer_artifact import build_installer_artifact
from packaging.upgrade_simulation import (
    UpgradeSimulationResult,
    simulate_upgrade,
)


def test_result_is_immutable(tmp_path):
    result = UpgradeSimulationResult(
        success=True,
        installation_root=tmp_path,
        executable=None,
        files_installed=0,
        configuration_preserved=True,
        logs_preserved=True,
        reports_preserved=True,
        shortcuts_preserved=True,
    )

    try:
        result.success = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "UpgradeSimulationResult must be immutable."
        )


def test_upgrade_replaces_application(tmp_path):
    artifact = build_installer_artifact()

    installation = tmp_path / "Windows Technician"
    installation.mkdir()

    old_file = installation / "old-runtime-marker.txt"
    old_file.write_text("old application", encoding="utf-8")

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=installation,
        installed_version="0.8.0",
    )

    assert result.success is True
    assert result.executable is not None
    assert result.executable.exists()
    assert result.files_installed > 1
    assert not old_file.exists()


def test_upgrade_preserves_configuration(tmp_path):
    artifact = build_installer_artifact()

    installation = tmp_path / "Windows Technician"
    configuration = tmp_path / "configuration"
    configuration.mkdir()

    marker = configuration / "settings.json"
    marker.write_text(
        '{"remediation_authorization": false}',
        encoding="utf-8",
    )

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=installation,
        installed_version="0.8.0",
        configuration_root=configuration,
    )

    assert result.success is True
    assert result.configuration_preserved is True
    assert marker.read_text(encoding="utf-8") == (
        '{"remediation_authorization": false}'
    )


def test_upgrade_preserves_logs(tmp_path):
    artifact = build_installer_artifact()

    logs = tmp_path / "logs"
    logs.mkdir()

    marker = logs / "application.log"
    marker.write_text("previous log", encoding="utf-8")

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        installed_version="0.8.0",
        logs_root=logs,
    )

    assert result.success is True
    assert result.logs_preserved is True
    assert marker.read_text(encoding="utf-8") == "previous log"


def test_upgrade_preserves_reports(tmp_path):
    artifact = build_installer_artifact()

    reports = tmp_path / "reports"
    reports.mkdir()

    marker = reports / "report.json"
    marker.write_text(
        '{"previous": true}',
        encoding="utf-8",
    )

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        installed_version="0.8.0",
        reports_root=reports,
    )

    assert result.success is True
    assert result.reports_preserved is True
    assert marker.read_text(encoding="utf-8") == '{"previous": true}'


def test_upgrade_preserves_shortcuts(tmp_path):
    artifact = build_installer_artifact()

    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()

    marker = shortcuts / "Windows Technician.lnk"
    marker.write_text("shortcut", encoding="utf-8")

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        installed_version="0.8.0",
        shortcuts_root=shortcuts,
    )

    assert result.success is True
    assert result.shortcuts_preserved is True
    assert marker.read_text(encoding="utf-8") == "shortcut"


def test_upgrade_rejects_downgrade(tmp_path):
    artifact = build_installer_artifact()

    result = simulate_upgrade(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        installed_version=APPLICATION_METADATA.version,
    )

    assert result.success is False
    assert any(
        "newer" in error
        for error in result.errors
    )


def test_upgrade_rejects_missing_artifact(tmp_path):
    result = simulate_upgrade(
        tmp_path / "missing.zip",
        installation_root=tmp_path / "Windows Technician",
        installed_version="0.8.0",
    )

    assert result.success is False
    assert result.files_installed == 0


def test_upgrade_rejects_non_zip(tmp_path):
    artifact = tmp_path / "upgrade.txt"
    artifact.write_text("invalid", encoding="utf-8")

    result = simulate_upgrade(
        artifact,
        installation_root=tmp_path / "Windows Technician",
        installed_version="0.8.0",
    )

    assert result.success is False
    assert any(
        "ZIP archive" in error
        for error in result.errors
    )
