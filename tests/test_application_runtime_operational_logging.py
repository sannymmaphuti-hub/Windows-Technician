from engine.application_logging import ApplicationLogger
from packaging.application_lifecycle import ApplicationLifecycleState
from packaging.application_runtime import (
    ApplicationRuntime,
    apply_runtime_recovery,
    create_application_runtime,
    start_application_runtime,
    stop_application_runtime,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)
from packaging.runtime_recovery import RecoveryAction


def build_logger(tmp_path):
    return RuntimeOperationalLogger(
        ApplicationLogger(tmp_path / "application.log")
    )


def test_runtime_accepts_operational_logger(tmp_path):
    logger = build_logger(tmp_path)

    runtime = create_application_runtime(
        operational_logger=logger,
    )

    assert runtime.operational_logger is logger


def test_runtime_rejects_invalid_operational_logger():
    try:
        create_application_runtime(
            operational_logger=object(),
        )
    except TypeError:
        pass
    else:
        raise AssertionError(
            "Invalid operational logger must be rejected."
        )


def test_runtime_start_logs_starting_and_running(tmp_path):
    logger = build_logger(tmp_path)

    runtime = create_application_runtime(
        operational_logger=logger,
    )

    started = start_application_runtime(runtime)

    assert started.lifecycle.state is ApplicationLifecycleState.RUNNING

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_STARTING]" in content
    assert "[APPLICATION_RUNNING]" in content


def test_runtime_stop_logs_stopping_and_stopped(tmp_path):
    logger = build_logger(tmp_path)

    runtime = create_application_runtime(
        operational_logger=logger,
    )
    runtime = start_application_runtime(runtime)
    runtime = stop_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_STOPPING]" in content
    assert "[APPLICATION_STOPPED]" in content


def test_runtime_degradation_logs_event(tmp_path):
    logger = build_logger(tmp_path)

    runtime = create_application_runtime(
        operational_logger=logger,
    )
    runtime = start_application_runtime(runtime)

    degraded = apply_runtime_recovery(
        runtime,
        RecoveryAction.DEGRADED,
    )

    assert degraded.lifecycle.state is ApplicationLifecycleState.DEGRADED

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[APPLICATION_DEGRADED]" in content
