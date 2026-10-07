"""Tests for deterministic uninstallation simulation."""

from packaging.uninstallation_simulation import (
    UninstallationSimulationResult,
    simulate_uninstallation,
)


def _create_installation(root):
    root.mkdir(parents=True)
    (root / "WindowsTechnician.exe").write_bytes(b"application")
    internal = root / "_internal"
    internal.mkdir()
    (internal / "runtime.dll").write_bytes(b"runtime")


def test_result_is_immutable(tmp_path):
    result = UninstallationSimulationResult(
        success=True,
        installation_root=tmp_path,
        application_removed=True,
        configuration_preserved=True,
        logs_preserved=True,
        reports_preserved=True,
        shortcuts_removed=True,
    )

    try:
        result.success = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "UninstallationSimulationResult must be immutable."
        )


def test_uninstall_removes_application(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    result = simulate_uninstallation(
        installation_root=installation,
    )

    assert result.success is True
    assert result.application_removed is True
    assert not installation.exists()


def test_uninstall_preserves_configuration(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    configuration = tmp_path / "configuration"
    configuration.mkdir()

    marker = configuration / "settings.json"
    marker.write_text(
        '{"remediation_authorization": false}',
        encoding="utf-8",
    )

    result = simulate_uninstallation(
        installation_root=installation,
        configuration_root=configuration,
    )

    assert result.success is True
    assert result.configuration_preserved is True
    assert marker.exists()


def test_uninstall_preserves_logs(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    logs = tmp_path / "logs"
    logs.mkdir()

    marker = logs / "application.log"
    marker.write_text(
        "previous log",
        encoding="utf-8",
    )

    result = simulate_uninstallation(
        installation_root=installation,
        logs_root=logs,
    )

    assert result.success is True
    assert result.logs_preserved is True
    assert marker.exists()


def test_uninstall_preserves_reports(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    reports = tmp_path / "reports"
    reports.mkdir()

    marker = reports / "report.json"
    marker.write_text(
        '{"previous": true}',
        encoding="utf-8",
    )

    result = simulate_uninstallation(
        installation_root=installation,
        reports_root=reports,
    )

    assert result.success is True
    assert result.reports_preserved is True
    assert marker.exists()


def test_uninstall_removes_shortcut(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()

    shortcut = shortcuts / "Windows Technician.lnk"
    shortcut.write_text("shortcut", encoding="utf-8")

    result = simulate_uninstallation(
        installation_root=installation,
        shortcuts_root=shortcuts,
    )

    assert result.success is True
    assert result.shortcuts_removed is True
    assert not shortcut.exists()


def test_uninstall_preserves_unrelated_shortcuts(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()

    technician = shortcuts / "Windows Technician.lnk"
    other = shortcuts / "Other Application.lnk"

    technician.write_text("technician", encoding="utf-8")
    other.write_text("other", encoding="utf-8")

    result = simulate_uninstallation(
        installation_root=installation,
        shortcuts_root=shortcuts,
    )

    assert result.success is True
    assert not technician.exists()
    assert other.exists()


def test_missing_installation_is_safe(tmp_path):
    installation = tmp_path / "Windows Technician"

    result = simulate_uninstallation(
        installation_root=installation,
    )

    assert result.success is True
    assert result.application_removed is True


def test_user_data_removal_is_not_normal_uninstall(tmp_path):
    installation = tmp_path / "Windows Technician"
    _create_installation(installation)

    configuration = tmp_path / "configuration"
    configuration.mkdir()

    marker = configuration / "settings.json"
    marker.write_text("protected", encoding="utf-8")

    result = simulate_uninstallation(
        installation_root=installation,
        configuration_root=configuration,
        remove_user_data=True,
    )

    assert result.success is False
    assert marker.exists()
    assert any(
        "destructive operation" in error
        for error in result.errors
    )


def test_non_directory_installation_root_is_rejected(tmp_path):
    installation = tmp_path / "Windows Technician"
    installation.write_text("not a directory", encoding="utf-8")

    result = simulate_uninstallation(
        installation_root=installation,
    )

    assert result.success is False
    assert any(
        "directory" in error
        for error in result.errors
    )
