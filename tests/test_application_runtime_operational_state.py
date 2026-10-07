from pathlib import Path

from packaging.application_lifecycle import (
    ApplicationLifecycleState,
)
from packaging.application_runtime import (
    ApplicationRuntime,
    create_application_runtime,
    start_application_runtime,
    stop_application_runtime,
)
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.runtime_configuration import RuntimePaths


def make_operational_state(tmp_path: Path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    return RuntimeOperationalState.from_runtime_paths(paths)


def test_runtime_can_be_created_without_operational_persistence():
    runtime = create_application_runtime()

    assert runtime.operational_state is None


def test_runtime_preserves_operational_state_boundary(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    runtime = create_application_runtime(
        operational_state=operational,
    )

    assert runtime.operational_state is operational


def test_start_persists_running_state(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    runtime = create_application_runtime(
        operational_state=operational,
    )

    runtime = start_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.RUNNING

    persisted = operational.store.load()

    assert persisted is not None
    assert persisted.lifecycle_state == "RUNNING"
    assert persisted.clean_shutdown is False


def test_stop_persists_clean_shutdown(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    runtime = create_application_runtime(
        operational_state=operational,
    )

    runtime = start_application_runtime(runtime)
    runtime = stop_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED

    persisted = operational.store.load()

    assert persisted is not None
    assert persisted.lifecycle_state == "STOPPED"
    assert persisted.clean_shutdown is True


def test_start_preserves_operational_state_after_transition(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    runtime = create_application_runtime(
        operational_state=operational,
    )

    updated = start_application_runtime(runtime)

    assert updated.operational_state is operational


def test_stop_preserves_operational_state_after_transition(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    runtime = create_application_runtime(
        operational_state=operational,
    )

    runtime = start_application_runtime(runtime)
    updated = stop_application_runtime(runtime)

    assert updated.operational_state is operational


def test_existing_runtime_without_persistence_still_works():
    runtime = create_application_runtime()

    runtime = start_application_runtime(runtime)
    runtime = stop_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED


def test_persistence_does_not_create_a_second_lifecycle():
    operational = make_operational_state(Path(".") / ".test-operational")

    runtime = create_application_runtime(
        operational_state=operational,
    )

    assert isinstance(runtime, ApplicationRuntime)
    assert isinstance(runtime.lifecycle.state, ApplicationLifecycleState)

    # The lifecycle remains the canonical source of runtime state.
    assert runtime.lifecycle.state is ApplicationLifecycleState.CREATED
