import pytest

from packaging.application_lifecycle import (
    ApplicationLifecycleState,
)
from packaging.application_runtime import (
    ApplicationRuntime,
    application_runtime_is_degraded,
    application_runtime_is_running,
    application_runtime_is_stopped,
    apply_runtime_recovery,
    create_application_runtime,
    start_application_runtime,
    stop_application_runtime,
)
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
    get_application_service,
)
from packaging.runtime_recovery import RecoveryAction


def test_runtime_starts_created():
    runtime = create_application_runtime()

    assert runtime.lifecycle.state is ApplicationLifecycleState.CREATED


def test_runtime_starts_with_all_services_unavailable():
    runtime = create_application_runtime()

    assert all(
        service.state is ApplicationServiceState.UNAVAILABLE
        for service in runtime.services.services
    )


def test_runtime_starts_successfully():
    runtime = create_application_runtime()

    runtime = start_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.RUNNING
    assert runtime.lifecycle.startup_completed is True


def test_runtime_start_marks_all_services_running():
    runtime = create_application_runtime()

    runtime = start_application_runtime(runtime)

    assert all(
        service.state is ApplicationServiceState.RUNNING
        for service in runtime.services.services
    )


def test_running_runtime_is_detected():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    assert application_runtime_is_running(runtime) is True


def test_created_runtime_is_not_running():
    runtime = create_application_runtime()

    assert application_runtime_is_running(runtime) is False


def test_runtime_can_enter_degraded_state():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = apply_runtime_recovery(
        runtime,
        RecoveryAction.DEGRADED,
    )

    assert runtime.lifecycle.state is ApplicationLifecycleState.DEGRADED
    assert application_runtime_is_degraded(runtime) is True


def test_specific_service_can_be_degraded():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = apply_runtime_recovery(
        runtime,
        RecoveryAction.DEGRADED,
        ApplicationServiceName.DIAGNOSTICS,
    )

    assert runtime.lifecycle.state is ApplicationLifecycleState.DEGRADED

    diagnostics = get_application_service(
        runtime.services,
        ApplicationServiceName.DIAGNOSTICS,
    )

    assert diagnostics.state is ApplicationServiceState.DEGRADED


def test_other_services_remain_running_when_one_degrades():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = apply_runtime_recovery(
        runtime,
        RecoveryAction.DEGRADED,
        ApplicationServiceName.DIAGNOSTICS,
    )

    logging = get_application_service(
        runtime.services,
        ApplicationServiceName.LOGGING,
    )

    assert logging.state is ApplicationServiceState.RUNNING


def test_continue_does_not_change_runtime():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    result = apply_runtime_recovery(
        runtime,
        RecoveryAction.CONTINUE,
    )

    assert result == runtime


def test_stop_recovery_does_not_fake_a_running_state():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    result = apply_runtime_recovery(
        runtime,
        RecoveryAction.STOP,
    )

    assert result == runtime
    assert application_runtime_is_running(result) is True


def test_degraded_runtime_can_stop():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = apply_runtime_recovery(
        runtime,
        RecoveryAction.DEGRADED,
        ApplicationServiceName.INTELLIGENCE,
    )

    runtime = stop_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED
    assert application_runtime_is_stopped(runtime) is True


def test_running_runtime_can_stop():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = stop_application_runtime(runtime)

    assert runtime.lifecycle.state is ApplicationLifecycleState.STOPPED
    assert runtime.lifecycle.shutdown_completed is True


def test_stopping_runtime_stops_all_services():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = stop_application_runtime(runtime)

    assert all(
        service.state is ApplicationServiceState.STOPPED
        for service in runtime.services.services
    )


def test_stopped_runtime_is_not_running():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    runtime = stop_application_runtime(runtime)

    assert application_runtime_is_running(runtime) is False


def test_starting_runtime_twice_is_rejected():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    with pytest.raises(ValueError):
        start_application_runtime(runtime)


def test_stopping_created_runtime_is_rejected():
    runtime = create_application_runtime()

    with pytest.raises(ValueError):
        stop_application_runtime(runtime)


def test_invalid_runtime_is_rejected():
    with pytest.raises(TypeError):
        start_application_runtime(None)


def test_invalid_recovery_action_is_rejected():
    runtime = create_application_runtime()

    with pytest.raises(TypeError):
        apply_runtime_recovery(
            runtime,
            "continue",
        )


def test_invalid_service_name_is_rejected():
    runtime = start_application_runtime(
        create_application_runtime()
    )

    with pytest.raises(TypeError):
        apply_runtime_recovery(
            runtime,
            RecoveryAction.DEGRADED,
            "diagnostics",
        )


def test_runtime_is_frozen():
    runtime = create_application_runtime()

    with pytest.raises(AttributeError):
        runtime.lifecycle = runtime.lifecycle


def test_runtime_stopped_helper_rejects_invalid_value():
    assert application_runtime_is_stopped(None) is False


def test_runtime_degraded_helper_rejects_invalid_value():
    assert application_runtime_is_degraded(None) is False


def test_runtime_running_helper_rejects_invalid_value():
    assert application_runtime_is_running(None) is False
