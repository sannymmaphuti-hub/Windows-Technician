from pathlib import Path

import pytest

from engine.application_bootstrap import ApplicationBootstrap
from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.runtime_configuration import RuntimePaths
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)


def make_operational_state(tmp_path: Path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    return RuntimeOperationalState.from_runtime_paths(paths)


def test_bootstrap_rejects_invalid_operational_state():
    with pytest.raises(TypeError):
        ApplicationBootstrap(
            operational_state="invalid"
        )


def test_bootstrap_without_operational_state_preserves_compatibility():
    bootstrap = ApplicationBootstrap()

    assert bootstrap.operational_state is None
    assert bootstrap.startup_recovery is None
    assert bootstrap.recovery_required is False
    assert bootstrap.runtime.operational_state is None


def test_bootstrap_accepts_operational_state(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    assert bootstrap.operational_state is operational
    assert bootstrap.runtime.operational_state is operational


def test_bootstrap_detects_fresh_start(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()

    assert bootstrap.startup_recovery is not None
    assert bootstrap.startup_recovery.recovery_required is False
    assert bootstrap.recovery_required is False
    assert bootstrap.started is True


def test_bootstrap_detects_unclean_previous_session(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()

    assert bootstrap.startup_recovery is not None
    assert bootstrap.startup_recovery.recovery_required is True
    assert bootstrap.recovery_required is True
    assert bootstrap.startup_recovery.previous_state.lifecycle_state == "RUNNING"


def test_bootstrap_detects_clean_previous_session(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()

    assert bootstrap.startup_recovery is not None
    assert bootstrap.startup_recovery.recovery_required is False
    assert bootstrap.recovery_required is False


def test_bootstrap_runtime_persists_new_running_state(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()

    assert bootstrap.runtime.lifecycle.state is (
        ApplicationLifecycleState.RUNNING
    )

    persisted = operational.store.load()

    assert persisted is not None
    assert persisted.lifecycle_state == "RUNNING"
    assert persisted.clean_shutdown is False


def test_bootstrap_stop_persists_clean_shutdown(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()
    bootstrap.stop()

    assert bootstrap.runtime.lifecycle.state is (
        ApplicationLifecycleState.STOPPED
    )

    persisted = operational.store.load()

    assert persisted is not None
    assert persisted.lifecycle_state == "STOPPED"
    assert persisted.clean_shutdown is True


def test_bootstrap_restart_after_stop_creates_recovery_aware_runtime(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()
    bootstrap.stop()
    bootstrap.start()

    assert bootstrap.started is True
    assert bootstrap.runtime.lifecycle.state is (
        ApplicationLifecycleState.RUNNING
    )
    assert bootstrap.runtime.operational_state is operational


def test_bootstrap_recovery_does_not_change_runtime_lifecycle_semantics(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    bootstrap = ApplicationBootstrap(
        operational_state=operational
    )

    bootstrap.start()

    assert bootstrap.recovery_required is True
    assert bootstrap.runtime.lifecycle.state is (
        ApplicationLifecycleState.RUNNING
    )
