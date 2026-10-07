from pathlib import Path

import pytest

from packaging.operational_state import OperationalStateStore
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.runtime_configuration import (
    RuntimePaths,
)


def make_runtime_paths(tmp_path: Path) -> RuntimePaths:
    return RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )


def test_runtime_operational_state_requires_store():
    with pytest.raises(TypeError):
        RuntimeOperationalState("invalid")


def test_runtime_operational_state_requires_runtime_paths():
    with pytest.raises(TypeError):
        RuntimeOperationalState.from_runtime_paths("invalid")


def test_runtime_operational_state_uses_canonical_runtime_path(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    assert operational.store.path == (
        paths.application_data
        / "operational_state.json"
    )


def test_runtime_operational_state_persists_running_state(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    state = operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    assert state.lifecycle_state == "RUNNING"
    assert state.clean_shutdown is False
    assert operational.store.path.exists()


def test_runtime_operational_state_persists_clean_shutdown(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    operational.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    restored = operational.store.load()

    assert restored is not None
    assert restored.lifecycle_state == "STOPPED"
    assert restored.clean_shutdown is True
    assert restored.recovered is False


def test_runtime_operational_state_recovers_unclean_session(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    recovered = operational.recover()

    assert recovered.lifecycle_state == "RUNNING"
    assert recovered.clean_shutdown is False
    assert recovered.recovered is True


def test_runtime_operational_state_does_not_mark_clean_session_as_recovered(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    operational.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    recovered = operational.recover()

    assert recovered.lifecycle_state == "STOPPED"
    assert recovered.clean_shutdown is True
    assert recovered.recovered is False


def test_runtime_operational_state_preserves_recovery_marker(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    state = operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
        recovered=True,
    )

    assert state.recovered is True

    restored = operational.store.load()

    assert restored is not None
    assert restored.recovered is True


def test_runtime_operational_state_round_trip_uses_store(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    operational.persist(
        lifecycle_state="STARTING",
        clean_shutdown=False,
    )

    direct_store = OperationalStateStore(
        paths.application_data
        / "operational_state.json"
    )

    restored = direct_store.load()

    assert restored is not None
    assert restored.lifecycle_state == "STARTING"
    assert restored.clean_shutdown is False


def test_runtime_operational_state_creates_runtime_directories(
    tmp_path: Path,
):
    paths = make_runtime_paths(tmp_path)

    RuntimeOperationalState.from_runtime_paths(paths)

    assert paths.application_data.exists()
    assert paths.configuration.exists()
    assert paths.logs.exists()
    assert paths.reports.exists()
