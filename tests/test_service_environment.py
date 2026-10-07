import pytest

from packaging.service_environment import (
    ServiceCompatibilityResult,
    ServiceEnvironment,
    ServiceEnvironmentLevel,
    ServiceState,
    classify_service_environment,
    evaluate_service_compatibility,
    service_compatibility_is_safe,
)


def make_service(
    state: ServiceState,
    name: str = "TestService",
) -> ServiceEnvironment:
    return ServiceEnvironment(
        service_name=name,
        state=state,
    )


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (ServiceState.RUNNING, ServiceEnvironmentLevel.HEALTHY),
        (ServiceState.STOPPED, ServiceEnvironmentLevel.INACTIVE),
        (ServiceState.FAILED, ServiceEnvironmentLevel.FAILED),
        (
            ServiceState.START_PENDING,
            ServiceEnvironmentLevel.TRANSITIONING,
        ),
        (
            ServiceState.STOP_PENDING,
            ServiceEnvironmentLevel.TRANSITIONING,
        ),
        (ServiceState.UNKNOWN, ServiceEnvironmentLevel.UNKNOWN),
    ],
)
def test_service_states_are_classified(
    state: ServiceState,
    expected: ServiceEnvironmentLevel,
) -> None:
    assert classify_service_environment(make_service(state)) is expected


@pytest.mark.parametrize("state", list(ServiceState))
def test_all_service_states_are_supported(
    state: ServiceState,
) -> None:
    result = evaluate_service_compatibility(make_service(state))

    assert result.compatible
    assert service_compatibility_is_safe(make_service(state))


def test_running_service_is_healthy() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.RUNNING)
    )

    assert result.level is ServiceEnvironmentLevel.HEALTHY
    assert "running" in result.reason.lower()


def test_stopped_service_is_not_treated_as_incompatible() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.STOPPED)
    )

    assert result.compatible
    assert result.level is ServiceEnvironmentLevel.INACTIVE
    assert "diagnos" in result.reason.lower()


def test_failed_service_is_not_treated_as_incompatible() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.FAILED)
    )

    assert result.compatible
    assert result.level is ServiceEnvironmentLevel.FAILED
    assert "diagnos" in result.reason.lower()


def test_failed_service_does_not_implicitly_remediate() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.FAILED)
    )

    assert result.compatible
    assert result.level is ServiceEnvironmentLevel.FAILED
    assert "changing the service" in result.reason.lower()


def test_unknown_service_state_is_safe_to_observe() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.UNKNOWN)
    )

    assert result.compatible
    assert result.level is ServiceEnvironmentLevel.UNKNOWN
    assert "unknown" in result.reason.lower()


def test_empty_service_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        ServiceEnvironment(
            service_name="",
            state=ServiceState.RUNNING,
        )


def test_whitespace_service_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        ServiceEnvironment(
            service_name="   ",
            state=ServiceState.RUNNING,
        )


def test_non_string_service_name_is_rejected() -> None:
    with pytest.raises(TypeError):
        ServiceEnvironment(
            service_name=123,
            state=ServiceState.RUNNING,
        )


def test_invalid_state_is_rejected() -> None:
    with pytest.raises(TypeError):
        ServiceEnvironment(
            service_name="TestService",
            state="RUNNING",
        )


def test_classification_requires_service_environment() -> None:
    with pytest.raises(TypeError):
        classify_service_environment(None)


def test_evaluation_requires_service_environment() -> None:
    with pytest.raises(TypeError):
        evaluate_service_compatibility(None)


def test_result_requires_boolean_compatibility() -> None:
    with pytest.raises(TypeError):
        ServiceCompatibilityResult(
            compatible="yes",
            level=ServiceEnvironmentLevel.HEALTHY,
            reason="invalid",
        )


def test_result_requires_valid_level() -> None:
    with pytest.raises(TypeError):
        ServiceCompatibilityResult(
            compatible=True,
            level="HEALTHY",
            reason="invalid",
        )


def test_result_requires_reason() -> None:
    with pytest.raises(ValueError):
        ServiceCompatibilityResult(
            compatible=True,
            level=ServiceEnvironmentLevel.HEALTHY,
            reason="",
        )


def test_service_environment_is_immutable() -> None:
    environment = make_service(ServiceState.RUNNING)

    with pytest.raises(AttributeError):
        environment.state = ServiceState.FAILED


def test_service_result_is_immutable() -> None:
    result = evaluate_service_compatibility(
        make_service(ServiceState.RUNNING)
    )

    with pytest.raises(AttributeError):
        result.compatible = False
