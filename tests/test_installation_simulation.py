"""Tests for deterministic installation simulation."""

from pathlib import Path

from packaging.installation_simulation import (
    InstallationSimulationResult,
    simulate_installation,
)
from packaging.installer_artifact import build_installer_artifact


def test_result_is_immutable(tmp_path):
    result = InstallationSimulationResult(
        success=True,
        installation_root=tmp_path,
        executable=None,
        files_installed=0,
        configuration_preserved=True,
        logs_preserved=True,
        reports_preserved=True,
    )

    try:
        result.success = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "InstallationSimulationResult must be immutable."
        )


def test_installation_copies_executable(tmp_path):
    artifact = build_installer_artifact()

    result = simulate_installation(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
    )

    assert result.success is True
    assert result.executable is not None
    assert result.executable.exists()
    assert result.files_installed > 1


def test_installation_copies_internal_runtime(tmp_path):
    artifact = build_installer_artifact()

    result = simulate_installation(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
    )

    assert result.success is True
    assert (
        result.installation_root / "_internal"
    ).is_dir()


def test_installation_preserves_configuration(tmp_path):
    artifact = build_installer_artifact()

    configuration = tmp_path / "configuration"
    configuration.mkdir()
    marker = configuration / "settings.json"
    marker.write_text('{"remediation_authorization": false}', encoding="utf-8")

    result = simulate_installation(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        configuration_root=configuration,
    )

    assert result.success is True
    assert result.configuration_preserved is True
    assert marker.read_text(encoding="utf-8") == (
        '{"remediation_authorization": false}'
    )


def test_installation_preserves_logs(tmp_path):
    artifact = build_installer_artifact()

    logs = tmp_path / "logs"
    logs.mkdir()
    marker = logs / "application.log"
    marker.write_text("existing log", encoding="utf-8")

    result = simulate_installation(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        logs_root=logs,
    )

    assert result.success is True
    assert result.logs_preserved is True
    assert marker.read_text(encoding="utf-8") == "existing log"


def test_installation_preserves_reports(tmp_path):
    artifact = build_installer_artifact()

    reports = tmp_path / "reports"
    reports.mkdir()
    marker = reports / "report.json"
    marker.write_text('{"existing": true}', encoding="utf-8")

    result = simulate_installation(
        artifact.artifact,
        installation_root=tmp_path / "Windows Technician",
        reports_root=reports,
    )

    assert result.success is True
    assert result.reports_preserved is True
    assert marker.read_text(encoding="utf-8") == '{"existing": true}'


def test_missing_artifact_is_rejected(tmp_path):
    result = simulate_installation(
        tmp_path / "missing.zip",
        installation_root=tmp_path / "Windows Technician",
    )

    assert result.success is False
    assert result.files_installed == 0


def test_non_zip_artifact_is_rejected(tmp_path):
    artifact = tmp_path / "installer.txt"
    artifact.write_text("not an installer", encoding="utf-8")

    result = simulate_installation(
        artifact,
        installation_root=tmp_path / "Windows Technician",
    )

    assert result.success is False
    assert any(
        "ZIP archive" in error
        for error in result.errors
    )
