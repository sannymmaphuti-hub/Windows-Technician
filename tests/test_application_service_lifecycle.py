import pytest

from packaging.application_lifecycle import (
    ApplicationLifecycleState,
    create_application_lifecycle,
)
from packaging.application_service_lifecycle import (
    ServiceLifecycleResult,
    degrade_application_service,
    start_application_services,
    stop_application_services,
)
from packaging.application_services import (
    ApplicationServiceName,
    ApplicationServiceState,
    create_application_service_registry,
    get_application_service,
)


def test_starting_services_moves_application_to_running():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    result = start_application_services(lifecycle, registry)

    assert result.lifecycle.state is ApplicationLifecycleState.RUNNING
    assert result.lifecycle.startup_completed is True


def test_starting_services_marks_every_service_running():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    result = start_application_services(lifecycle, registry)

    assert all(
        service.state is ApplicationServiceState.RUNNING
        for service in result.registry.services
    )


def test_starting_services_preserves_all_service_names():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    result = start_application_services(lifecycle, registry)

    assert {
        service.name
        for service in result.registry.services
    } == set(ApplicationServiceName)


def test_degrading_service_moves_application_to_degraded():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    result = degrade_application_service(
        started.lifecycle,
        started.registry,
        ApplicationServiceName.DIAGNOSTICS,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.DEGRADED


def test_degrading_service_marks_only_target_service():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    result = degrade_application_service(
        started.lifecycle,
        started.registry,
        ApplicationServiceName.DIAGNOSTICS,
    )

    diagnostics = get_application_service(
        result.registry,
        ApplicationServiceName.DIAGNOSTICS,
    )
    logging = get_application_service(
        result.registry,
        ApplicationServiceName.LOGGING,
    )

    assert diagnostics.state is ApplicationServiceState.DEGRADED
    assert logging.state is ApplicationServiceState.RUNNING


def test_stopping_services_moves_application_to_stopped():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    result = stop_application_services(
        started.lifecycle,
        started.registry,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.STOPPED
    assert result.lifecycle.shutdown_completed is True


def test_stopping_services_marks_every_service_stopped():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    result = stop_application_services(
        started.lifecycle,
        started.registry,
    )

    assert all(
        service.state is ApplicationServiceState.STOPPED
        for service in result.registry.services
    )


def test_service_lifecycle_result_is_frozen():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    result = ServiceLifecycleResult(
        lifecycle=lifecycle,
        registry=registry,
    )

    with pytest.raises(AttributeError):
        result.lifecycle = lifecycle


def test_invalid_lifecycle_is_rejected():
    registry = create_application_service_registry()

    with pytest.raises(TypeError):
        start_application_services(None, registry)


def test_invalid_registry_is_rejected():
    lifecycle = create_application_lifecycle()

    with pytest.raises(TypeError):
        start_application_services(lifecycle, None)


def test_invalid_service_name_is_rejected():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    with pytest.raises(TypeError):
        degrade_application_service(
            lifecycle,
            registry,
            "diagnostics",
        )


def test_degraded_service_can_be_stopped():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    degraded = degrade_application_service(
        started.lifecycle,
        started.registry,
        ApplicationServiceName.DIAGNOSTICS,
    )

    stopped = stop_application_services(
        degraded.lifecycle,
        degraded.registry,
    )

    assert stopped.lifecycle.state is ApplicationLifecycleState.STOPPED
    assert all(
        service.state is ApplicationServiceState.STOPPED
        for service in stopped.registry.services
    )


def test_degraded_application_is_not_claimed_running():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    result = degrade_application_service(
        started.lifecycle,
        started.registry,
        ApplicationServiceName.INTELLIGENCE,
    )

    assert result.lifecycle.state is not ApplicationLifecycleState.RUNNING


def test_start_requires_created_lifecycle():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    started = start_application_services(lifecycle, registry)

    with pytest.raises(ValueError):
        start_application_services(
            started.lifecycle,
            started.registry,
        )


def test_stop_requires_running_or_degraded_lifecycle():
    lifecycle = create_application_lifecycle()
    registry = create_application_service_registry()

    with pytest.raises(ValueError):
        stop_application_services(lifecycle, registry)
