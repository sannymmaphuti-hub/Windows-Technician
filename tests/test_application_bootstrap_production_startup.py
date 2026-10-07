"""Tests for production startup orchestration."""

from pathlib import Path

import pytest

from engine.application_bootstrap import ApplicationBootstrap
from engine.application_logging import ApplicationLogger
from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.production_configuration import (
    ProductionConfiguration,
)
from packaging.application_runtime_configuration import (
    RuntimeConfigurationState,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.operational_state import (
    OperationalStateStore,
)
from packaging.runtime_configuration import RuntimePaths


def _operational_state(tmp_path: Path):
    paths = RuntimePaths(
        application_data=tmp_path / "application",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    paths.application_data.mkdir(parents=True)

    return RuntimeOperationalState.from_runtime_paths(
        paths
    )


def _logger(tmp_path: Path):
    return RuntimeOperationalLogger(
        ApplicationLogger(
            tmp_path / "logs" / "application.log"
        )
    )


def _safe_configuration():
    return ProductionConfiguration(
        state=RuntimeConfigurationState(
            configuration={
                "version": 1,
                "diagnostics": {
                    "automatic_collection": True,
                },
                "remediation": {
                    "authorized_by_default": False,
                },
                "remote": {
                    "enabled": False,
                },
                "telemetry": {
                    "enabled": False,
                },
            },
            recovered=False,
            safe=True,
        )
    )


def _unsafe_configuration():
    return ProductionConfiguration(
        state=RuntimeConfigurationState(
            configuration={
                "version": 1,
            },
            recovered=False,
            safe=False,
        )
    )


def test_bootstrap_accepts_production_configuration(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    assert bootstrap.configuration is not None
    assert bootstrap.startup_allowed is True


def test_safe_configuration_allows_runtime_start(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    runtime = bootstrap.start()

    assert bootstrap.started is True
    assert runtime.lifecycle.state is ApplicationLifecycleState.RUNNING
    assert bootstrap.configuration_result is not None
    assert bootstrap.configuration_result.startup_allowed is True


def test_unsafe_configuration_blocks_runtime_start(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_unsafe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    runtime = bootstrap.start()

    assert bootstrap.started is False
    assert runtime.lifecycle.state is ApplicationLifecycleState.CREATED
    assert bootstrap.configuration_result is not None
    assert bootstrap.configuration_result.startup_allowed is False


def test_blocked_start_does_not_start_services(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_unsafe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    runtime = bootstrap.start()

    for service in runtime.services.services:
        assert service.state.name == "UNAVAILABLE"


def test_safe_configuration_is_applied_before_start(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    bootstrap.start()

    assert bootstrap.configuration_result is not None
    assert bootstrap.configuration_result.configuration is (
        bootstrap.configuration
    )


def test_operational_logger_is_preserved_through_start(tmp_path):
    logger = _logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=_operational_state(tmp_path),
        operational_logger=logger,
    )

    runtime = bootstrap.start()

    assert runtime.operational_logger is logger


def test_blocked_start_logs_failure(tmp_path):
    logger = _logger(tmp_path)

    bootstrap = ApplicationBootstrap(
        configuration=_unsafe_configuration(),
        operational_state=_operational_state(tmp_path),
        operational_logger=logger,
    )

    bootstrap.start()

    log_path = tmp_path / "logs" / "application.log"

    assert log_path.exists()

    content = log_path.read_text(
        encoding="utf-8"
    )

    assert "APPLICATION_FAILED" in content
    assert "startup blocked" in content.lower()


def test_recovery_detection_remains_intact(tmp_path):
    operational_state = _operational_state(tmp_path)

    operational_state.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=operational_state,
    )

    bootstrap.start()

    assert bootstrap.recovery_required is True


def test_clean_start_does_not_require_recovery(tmp_path):
    operational_state = _operational_state(tmp_path)

    operational_state.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=operational_state,
    )

    bootstrap.start()

    assert bootstrap.recovery_required is False


def test_stop_after_successful_start_remains_clean(tmp_path):
    bootstrap = ApplicationBootstrap(
        configuration=_safe_configuration(),
        operational_state=_operational_state(tmp_path),
    )

    bootstrap.start()
    runtime = bootstrap.stop()

    assert bootstrap.started is False
    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED
