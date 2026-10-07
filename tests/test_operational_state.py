from pathlib import Path

import pytest

from packaging.operational_state import (
    OperationalState,
    OperationalStateStore,
    operational_state_path,
)


def test_operational_state_defaults_are_safe():
    state = OperationalState()

    assert state.schema_version == 1
    assert state.lifecycle_state == "CREATED"
    assert state.clean_shutdown is False
    assert state.recovered is False


def test_operational_state_rejects_invalid_schema_version():
    with pytest.raises(ValueError):
        OperationalState(schema_version=0)


def test_operational_state_rejects_invalid_lifecycle_state():
    with pytest.raises(ValueError):
        OperationalState(lifecycle_state="   ")


def test_operational_state_rejects_invalid_clean_shutdown():
    with pytest.raises(TypeError):
        OperationalState(clean_shutdown="yes")


def test_operational_state_round_trips_through_store(
    tmp_path: Path,
):
    path = tmp_path / "operational_state.json"
    store = OperationalStateStore(path)

    original = OperationalState(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
        recovered=False,
    )

    store.save(original)

    restored = store.load()

    assert restored == original


def test_store_creates_parent_directory(tmp_path: Path):
    path = (
        tmp_path
        / "nested"
        / "state"
        / "operational_state.json"
    )

    store = OperationalStateStore(path)
    store.save(OperationalState())

    assert path.exists()
    assert path.is_file()


def test_missing_state_recovers_as_fresh_runtime(
    tmp_path: Path,
):
    store = OperationalStateStore(
        tmp_path / "operational_state.json"
    )

    recovered = store.recover()

    assert recovered.lifecycle_state == "CREATED"
    assert recovered.clean_shutdown is False
    assert recovered.recovered is False


def test_unclean_previous_session_is_marked_recovered(
    tmp_path: Path,
):
    path = tmp_path / "operational_state.json"
    store = OperationalStateStore(path)

    store.save(
        OperationalState(
            lifecycle_state="RUNNING",
            clean_shutdown=False,
            recovered=False,
        )
    )

    recovered = store.recover()

    assert recovered.lifecycle_state == "RUNNING"
    assert recovered.clean_shutdown is False
    assert recovered.recovered is True


def test_clean_previous_session_does_not_fake_recovery(
    tmp_path: Path,
):
    path = tmp_path / "operational_state.json"
    store = OperationalStateStore(path)

    store.save(
        OperationalState(
            lifecycle_state="STOPPED",
            clean_shutdown=True,
            recovered=False,
        )
    )

    recovered = store.recover()

    assert recovered.lifecycle_state == "STOPPED"
    assert recovered.clean_shutdown is True
    assert recovered.recovered is False


def test_corrupt_state_is_rejected(tmp_path: Path):
    path = tmp_path / "operational_state.json"
    path.write_text(
        "{not valid json",
        encoding="utf-8",
    )

    store = OperationalStateStore(path)

    with pytest.raises(ValueError):
        store.load()


def test_non_object_state_is_rejected(tmp_path: Path):
    path = tmp_path / "operational_state.json"
    path.write_text(
        "[]",
        encoding="utf-8",
    )

    store = OperationalStateStore(path)

    with pytest.raises(ValueError):
        store.load()


def test_operational_state_path_uses_application_data_root():
    class RuntimePaths:
        application_data = Path("runtime-root")

    assert (
        operational_state_path(RuntimePaths())
        == Path("runtime-root") / "operational_state.json"
    )
