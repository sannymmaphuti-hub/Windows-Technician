"""Integration tests for runtime reliability."""

from packaging.runtime_reliability import (
    RuntimeReliabilityResult,
    initialize_runtime_reliability,
    runtime_reliability_is_healthy,
)
from packaging.runtime_recovery import RecoveryAction


def test_healthy_runtime_is_reported():
    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=__import__("pathlib").Path(
            __import__("pathlib").Path.cwd()
            / "test-runtime-settings.json"
        ),
        dependency_names=("json",),
    )

    assert isinstance(result, RuntimeReliabilityResult)
    assert result.startup.succeeded is True
    assert result.operation.succeeded is True
    assert result.dependencies[0].available is True
    assert result.recovery.action is RecoveryAction.CONTINUE


def test_runtime_operation_failure_is_integrated(tmp_path):
    def failing_operation():
        raise RuntimeError("runtime failure")

    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="failing operation",
        operation_callable=failing_operation,
        configuration_path=tmp_path / "settings.json",
        dependency_names=("json",),
    )

    assert result.operation.succeeded is False
    assert result.recovery.action is RecoveryAction.CONTINUE


def test_missing_dependency_is_integrated(tmp_path):
    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=tmp_path / "settings.json",
        dependency_names=(
            "json",
            "windows_technician_missing_dependency",
        ),
    )

    assert result.dependencies[0].available is True
    assert result.dependencies[1].available is False
    assert result.recovery.action is RecoveryAction.DEGRADED


def test_startup_failure_is_integrated(tmp_path):
    def failing_startup():
        raise RuntimeError("startup failure")

    result = initialize_runtime_reliability(
        startup_callable=failing_startup,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=tmp_path / "settings.json",
        dependency_names=("json",),
    )

    assert result.startup.succeeded is False
    assert result.recovery.action is RecoveryAction.STOP


def test_corrupt_configuration_is_integrated(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(
        '{"broken": ',
        encoding="utf-8",
    )

    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=path,
        dependency_names=("json",),
    )

    assert result.configuration.recovered is True
    assert result.configuration.quarantined_path is not None


def test_healthy_runtime_requires_no_recovery(tmp_path):
    path = tmp_path / "settings.json"

    path.write_text(
        '{"version": 1}',
        encoding="utf-8",
    )

    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=path,
        dependency_names=("json",),
    )

    assert runtime_reliability_is_healthy(result) is True


def test_recovered_configuration_is_not_healthy(tmp_path):
    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="health check",
        operation_callable=lambda: "ok",
        configuration_path=tmp_path / "missing.json",
        dependency_names=("json",),
    )

    assert runtime_reliability_is_healthy(result) is False


def test_failed_operation_is_not_healthy(tmp_path):
    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="operation",
        operation_callable=lambda: (_ for _ in ()).throw(
            RuntimeError("failed")
        ),
        configuration_path=tmp_path / "settings.json",
        dependency_names=("json",),
    )

    assert runtime_reliability_is_healthy(result) is False


def test_result_is_immutable(tmp_path):
    result = initialize_runtime_reliability(
        startup_callable=lambda: None,
        operation_name="operation",
        operation_callable=lambda: "ok",
        configuration_path=tmp_path / "settings.json",
        dependency_names=("json",),
    )

    try:
        result.recovery = result.recovery
        assert False
    except AttributeError:
        pass
