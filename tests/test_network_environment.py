import pytest

from packaging.network_environment import (
    NetworkCompatibilityResult,
    NetworkEnvironment,
    NetworkEnvironmentLevel,
    NetworkState,
    classify_network_environment,
    evaluate_network_compatibility,
    network_compatibility_is_safe,
)


def make_network(
    state: NetworkState,
) -> NetworkEnvironment:
    return NetworkEnvironment(state=state)


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (
            NetworkState.AVAILABLE,
            NetworkEnvironmentLevel.CONNECTED,
        ),
        (
            NetworkState.DEGRADED,
            NetworkEnvironmentLevel.DEGRADED,
        ),
        (
            NetworkState.UNAVAILABLE,
            NetworkEnvironmentLevel.OFFLINE,
        ),
        (
            NetworkState.UNKNOWN,
            NetworkEnvironmentLevel.UNKNOWN,
        ),
    ],
)
def test_network_states_are_classified(
    state: NetworkState,
    expected: NetworkEnvironmentLevel,
) -> None:
    assert classify_network_environment(
        make_network(state)
    ) is expected


@pytest.mark.parametrize("state", list(NetworkState))
def test_all_network_states_are_supported(
    state: NetworkState,
) -> None:
    environment = make_network(state)

    result = evaluate_network_compatibility(environment)

    assert result.compatible
    assert network_compatibility_is_safe(environment)


def test_available_network_is_connected() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.AVAILABLE)
    )

    assert result.level is NetworkEnvironmentLevel.CONNECTED
    assert "available" in result.reason.lower()


def test_degraded_network_remains_usable() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.DEGRADED)
    )

    assert result.compatible
    assert result.level is NetworkEnvironmentLevel.DEGRADED
    assert "degraded" in result.reason.lower()


def test_unavailable_network_does_not_break_local_diagnostics() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.UNAVAILABLE)
    )

    assert result.compatible
    assert result.level is NetworkEnvironmentLevel.OFFLINE
    assert "local diagnostics" in result.reason.lower()


def test_unavailable_network_blocks_only_network_dependent_operations() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.UNAVAILABLE)
    )

    assert result.compatible
    assert "network-dependent operations" in result.reason.lower()


def test_unknown_network_state_is_safe_to_observe() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.UNKNOWN)
    )

    assert result.compatible
    assert result.level is NetworkEnvironmentLevel.UNKNOWN
    assert "unknown" in result.reason.lower()


def test_invalid_network_state_is_rejected() -> None:
    with pytest.raises(TypeError):
        NetworkEnvironment(state="AVAILABLE")


def test_classification_requires_network_environment() -> None:
    with pytest.raises(TypeError):
        classify_network_environment(None)


def test_evaluation_requires_network_environment() -> None:
    with pytest.raises(TypeError):
        evaluate_network_compatibility(None)


def test_result_requires_boolean_compatibility() -> None:
    with pytest.raises(TypeError):
        NetworkCompatibilityResult(
            compatible="yes",
            level=NetworkEnvironmentLevel.CONNECTED,
            reason="invalid",
        )


def test_result_requires_valid_level() -> None:
    with pytest.raises(TypeError):
        NetworkCompatibilityResult(
            compatible=True,
            level="CONNECTED",
            reason="invalid",
        )


def test_result_requires_reason() -> None:
    with pytest.raises(ValueError):
        NetworkCompatibilityResult(
            compatible=True,
            level=NetworkEnvironmentLevel.CONNECTED,
            reason="",
        )


def test_network_environment_is_immutable() -> None:
    environment = make_network(NetworkState.AVAILABLE)

    with pytest.raises(AttributeError):
        environment.state = NetworkState.UNAVAILABLE


def test_network_result_is_immutable() -> None:
    result = evaluate_network_compatibility(
        make_network(NetworkState.AVAILABLE)
    )

    with pytest.raises(AttributeError):
        result.compatible = False
