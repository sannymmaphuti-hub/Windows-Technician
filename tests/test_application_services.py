import pytest

from packaging.application_services import (
    ApplicationService,
    ApplicationServiceName,
    ApplicationServiceRegistry,
    ApplicationServiceState,
    application_service_registry_healthy,
    create_application_service_registry,
    get_application_service,
    update_application_service,
)


def test_registry_contains_all_application_services():
    registry = create_application_service_registry()

    assert len(registry.services) == len(ApplicationServiceName)

    assert {
        service.name
        for service in registry.services
    } == set(ApplicationServiceName)


def test_services_start_unavailable():
    registry = create_application_service_registry()

    assert all(
        service.state is ApplicationServiceState.UNAVAILABLE
        for service in registry.services
    )


def test_service_can_be_updated():
    registry = create_application_service_registry()

    registry = update_application_service(
        registry,
        ApplicationServiceName.DIAGNOSTICS,
        ApplicationServiceState.RUNNING,
    )

    service = get_application_service(
        registry,
        ApplicationServiceName.DIAGNOSTICS,
    )

    assert service.state is ApplicationServiceState.RUNNING


def test_update_does_not_change_other_services():
    registry = create_application_service_registry()

    registry = update_application_service(
        registry,
        ApplicationServiceName.DIAGNOSTICS,
        ApplicationServiceState.RUNNING,
    )

    logging_service = get_application_service(
        registry,
        ApplicationServiceName.LOGGING,
    )

    assert logging_service.state is ApplicationServiceState.UNAVAILABLE


def test_registry_is_unhealthy_until_all_services_run():
    registry = create_application_service_registry()

    assert application_service_registry_healthy(registry) is False


def test_registry_is_healthy_when_all_services_run():
    registry = create_application_service_registry()

    for name in ApplicationServiceName:
        registry = update_application_service(
            registry,
            name,
            ApplicationServiceState.RUNNING,
        )

    assert application_service_registry_healthy(registry) is True


def test_registry_is_frozen():
    registry = create_application_service_registry()

    with pytest.raises(AttributeError):
        registry.services = ()


def test_service_is_frozen():
    service = ApplicationService(
        name=ApplicationServiceName.UI,
        state=ApplicationServiceState.RUNNING,
    )

    with pytest.raises(AttributeError):
        service.state = ApplicationServiceState.FAILED


def test_duplicate_service_names_are_rejected():
    service = ApplicationService(
        name=ApplicationServiceName.UI,
        state=ApplicationServiceState.RUNNING,
    )

    with pytest.raises(ValueError):
        ApplicationServiceRegistry(
            services=(service, service),
        )


def test_invalid_registry_type_is_rejected():
    with pytest.raises(TypeError):
        update_application_service(
            None,
            ApplicationServiceName.UI,
            ApplicationServiceState.RUNNING,
        )


def test_invalid_service_name_is_rejected():
    registry = create_application_service_registry()

    with pytest.raises(TypeError):
        update_application_service(
            registry,
            "ui",
            ApplicationServiceState.RUNNING,
        )


def test_invalid_service_state_is_rejected():
    registry = create_application_service_registry()

    with pytest.raises(TypeError):
        update_application_service(
            registry,
            ApplicationServiceName.UI,
            "running",
        )


def test_get_invalid_service_name_is_rejected():
    registry = create_application_service_registry()

    with pytest.raises(TypeError):
        get_application_service(registry, "ui")


def test_healthy_check_rejects_invalid_registry():
    assert application_service_registry_healthy(None) is False
