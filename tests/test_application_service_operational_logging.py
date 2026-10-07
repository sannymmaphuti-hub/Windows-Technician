from engine.application_logging import ApplicationLogger
from packaging.application_lifecycle import (
    ApplicationLifecycleState,
    create_application_lifecycle,
)
from packaging.application_service_lifecycle import (
    degrade_application_service,
    start_application_services,
    stop_application_services,
)
from packaging.application_services import (
    ApplicationServiceName,
    create_application_service_registry,
)
from packaging.runtime_operational_logging import (
    RuntimeOperationalLogger,
)


def build_logger(tmp_path):
    return RuntimeOperationalLogger(
        ApplicationLogger(tmp_path / "application.log")
    )


def build_state():
    return (
        create_application_lifecycle(),
        create_application_service_registry(),
    )


def test_start_application_services_logs_service_start_events(tmp_path):
    logger = build_logger(tmp_path)
    lifecycle, registry = build_state()

    result = start_application_services(
        lifecycle,
        registry,
        logger,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.RUNNING

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    for name in ApplicationServiceName:
        assert "[SERVICE_STARTING]" in content
        assert "[SERVICE_STARTED]" in content
        assert name.name in content


def test_stop_application_services_logs_service_stop_events(tmp_path):
    logger = build_logger(tmp_path)
    lifecycle, registry = build_state()

    started = start_application_services(
        lifecycle,
        registry,
        logger,
    )

    stopped = stop_application_services(
        started.lifecycle,
        started.registry,
        logger,
    )

    assert stopped.lifecycle.state is ApplicationLifecycleState.STOPPED

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    for name in ApplicationServiceName:
        assert "[SERVICE_STOPPING]" in content
        assert "[SERVICE_STOPPED]" in content
        assert name.name in content


def test_degrade_application_service_logs_service_event(tmp_path):
    logger = build_logger(tmp_path)
    lifecycle, registry = build_state()

    started = start_application_services(
        lifecycle,
        registry,
        logger,
    )

    result = degrade_application_service(
        started.lifecycle,
        started.registry,
        ApplicationServiceName.DIAGNOSTICS,
        logger,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.DEGRADED

    content = (
        tmp_path / "application.log"
    ).read_text(encoding="utf-8")

    assert "[SERVICE_DEGRADED]" in content
    assert "DIAGNOSTICS" in content
    assert "WARNING" in content


def test_service_lifecycle_remains_backward_compatible(tmp_path):
    lifecycle, registry = build_state()

    result = start_application_services(
        lifecycle,
        registry,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.RUNNING

    result = stop_application_services(
        result.lifecycle,
        result.registry,
    )

    assert result.lifecycle.state is ApplicationLifecycleState.STOPPED
