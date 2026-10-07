from pathlib import Path

import pytest

from packaging.operational_state import OperationalState
from packaging.runtime_configuration import RuntimePaths
from packaging.runtime_operational_state import (
    RuntimeOperationalState,
)
from packaging.startup_recovery import (
    StartupRecoveryContext,
    build_startup_recovery_context,
    startup_recovery_is_required,
    startup_recovery_was_clean,
)


def make_operational_state(tmp_path: Path):
    paths = RuntimePaths(
        application_data=tmp_path / "app",
        configuration=tmp_path / "config",
        logs=tmp_path / "logs",
        reports=tmp_path / "reports",
    )

    return RuntimeOperationalState.from_runtime_paths(paths)


def test_startup_recovery_context_requires_operational_state():
    with pytest.raises(TypeError):
        build_startup_recovery_context("invalid")


def test_missing_previous_state_does_not_require_recovery(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    context = build_startup_recovery_context(operational)

    assert isinstance(context, StartupRecoveryContext)
    assert context.recovery_required is False
    assert context.previous_state.lifecycle_state == "CREATED"
    assert context.previous_state.recovered is False


def test_clean_previous_shutdown_does_not_require_recovery(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    context = build_startup_recovery_context(operational)

    assert context.recovery_required is False
    assert context.previous_state.clean_shutdown is True


def test_unclean_previous_shutdown_requires_recovery(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    context = build_startup_recovery_context(operational)

    assert context.recovery_required is True
    assert context.previous_state.lifecycle_state == "RUNNING"
    assert context.previous_state.clean_shutdown is False
    assert context.previous_state.recovered is True


def test_recovery_required_helper(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    context = build_startup_recovery_context(operational)

    assert startup_recovery_is_required(context) is True


def test_clean_shutdown_helper(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="STOPPED",
        clean_shutdown=True,
    )

    context = build_startup_recovery_context(operational)

    assert startup_recovery_was_clean(context) is True


def test_recovery_context_does_not_modify_previous_state(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)

    operational.persist(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
    )

    context = build_startup_recovery_context(operational)

    assert context.previous_state == OperationalState(
        lifecycle_state="RUNNING",
        clean_shutdown=False,
        recovered=True,
    )

    persisted = operational.store.load()

    assert persisted is not None
    assert persisted.lifecycle_state == "RUNNING"
    assert persisted.clean_shutdown is False
    assert persisted.recovered is False


def test_invalid_recovery_context_is_rejected():
    with pytest.raises(TypeError):
        StartupRecoveryContext(
            previous_state="invalid",
            recovery_required=False,
        )


def test_recovery_context_requires_boolean_flag(
    tmp_path: Path,
):
    operational = make_operational_state(tmp_path)
    state = operational.recover()

    with pytest.raises(TypeError):
        StartupRecoveryContext(
            previous_state=state,
            recovery_required="yes",
        )
