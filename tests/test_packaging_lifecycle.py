"""End-to-end tests for the production packaging lifecycle."""

from packaging.packaging_lifecycle import (
    PackagingLifecycleResult,
    run_packaging_lifecycle,
)


def test_lifecycle_result_is_immutable(tmp_path):
    result = PackagingLifecycleResult(
        success=True,
        artifact_created=True,
        archive_valid=True,
        installation_successful=True,
        runtime_valid=True,
        upgrade_successful=True,
        upgraded_runtime_valid=True,
        uninstallation_successful=True,
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
            "PackagingLifecycleResult must be immutable."
        )


def test_complete_packaging_lifecycle(tmp_path):
    result = run_packaging_lifecycle(
        workspace=tmp_path,
    )

    assert result.success is True
    assert result.artifact_created is True
    assert result.archive_valid is True
    assert result.installation_successful is True
    assert result.runtime_valid is True
    assert result.upgrade_successful is True
    assert result.upgraded_runtime_valid is True
    assert result.uninstallation_successful is True
    assert result.configuration_preserved is True
    assert result.logs_preserved is True
    assert result.reports_preserved is True
    assert result.errors == ()


def test_lifecycle_removes_application_after_uninstall(tmp_path):
    result = run_packaging_lifecycle(
        workspace=tmp_path,
    )

    assert result.success is True
    assert not (
        tmp_path / "installed" / "Windows Technician"
    ).exists()


def test_lifecycle_preserves_user_data_after_uninstall(tmp_path):
    result = run_packaging_lifecycle(
        workspace=tmp_path,
    )

    assert result.success is True

    user_data = tmp_path / "user-data"

    assert (user_data / "configuration" / "settings.json").exists()
    assert (user_data / "logs" / "application.log").exists()
    assert (user_data / "reports" / "diagnostic-report.json").exists()
