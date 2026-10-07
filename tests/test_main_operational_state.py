from pathlib import Path

from packaging.runtime_configuration import RuntimePaths
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)


def test_production_operational_state_uses_runtime_paths(
    tmp_path: Path,
):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    assert operational.store.path == (
        paths.application_data
        / "operational_state.json"
    )


def test_production_operational_state_starts_without_previous_session(
    tmp_path: Path,
):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    operational = RuntimeOperationalState.from_runtime_paths(
        paths
    )

    recovered = operational.recover()

    assert recovered.lifecycle_state == "CREATED"
    assert recovered.clean_shutdown is False
    assert recovered.recovered is False


def test_production_operational_state_detects_previous_unclean_session(
    tmp_path: Path,
):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

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


def test_production_operational_state_detects_clean_previous_session(
    tmp_path: Path,
):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

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
