import pytest

from packaging.application_runtime import (
    ApplicationRuntime,
    create_application_runtime,
)
from packaging.application_runtime_configuration import (
    ConfigurationRuntimeResult,
    RuntimeConfigurationState,
    apply_configuration_to_runtime,
    configuration_allows_startup,
    configuration_is_safe,
    configuration_was_recovered,
    runtime_configuration_is_startable,
)


def test_safe_configuration_allows_startup():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={"mode": "safe"},
        recovered=False,
        safe=True,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert result.startup_allowed is True
    assert configuration_allows_startup(result) is True


def test_recovered_safe_configuration_allows_startup():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={"mode": "defaults"},
        recovered=True,
        safe=True,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert result.startup_allowed is True
    assert configuration_was_recovered(result) is True


def test_unsafe_configuration_blocks_startup():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={"mode": "invalid"},
        recovered=False,
        safe=False,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert result.startup_allowed is False
    assert configuration_allows_startup(result) is False


def test_configuration_safety_is_preserved():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={"mode": "safe"},
        recovered=True,
        safe=True,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert configuration_is_safe(result) is True


def test_configuration_recovery_state_is_preserved():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={"mode": "defaults"},
        recovered=True,
        safe=True,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert result.configuration is configuration
    assert result.configuration.recovered is True


def test_runtime_is_preserved():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    result = apply_configuration_to_runtime(
        runtime,
        configuration,
    )

    assert result.runtime is runtime


def test_runtime_configuration_state_is_frozen():
    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    with pytest.raises(AttributeError):
        configuration.safe = False


def test_configuration_runtime_result_is_frozen():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    result = ConfigurationRuntimeResult(
        runtime=runtime,
        configuration=configuration,
        startup_allowed=True,
    )

    with pytest.raises(AttributeError):
        result.startup_allowed = False


def test_invalid_runtime_is_rejected():
    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    with pytest.raises(TypeError):
        apply_configuration_to_runtime(
            None,
            configuration,
        )


def test_invalid_configuration_is_rejected():
    runtime = create_application_runtime()

    with pytest.raises(TypeError):
        apply_configuration_to_runtime(
            runtime,
            None,
        )


def test_invalid_recovered_value_is_rejected():
    with pytest.raises(TypeError):
        RuntimeConfigurationState(
            configuration={},
            recovered="yes",
            safe=True,
        )


def test_invalid_safe_value_is_rejected():
    with pytest.raises(TypeError):
        RuntimeConfigurationState(
            configuration={},
            recovered=False,
            safe="yes",
        )


def test_startable_configuration_requires_safety():
    unsafe = RuntimeConfigurationState(
        configuration={},
        recovered=True,
        safe=False,
    )

    assert runtime_configuration_is_startable(unsafe) is False


def test_startable_configuration_accepts_safe_defaults():
    safe = RuntimeConfigurationState(
        configuration={},
        recovered=True,
        safe=True,
    )

    assert runtime_configuration_is_startable(safe) is True


def test_helpers_reject_invalid_values():
    assert configuration_allows_startup(None) is False
    assert configuration_was_recovered(None) is False
    assert configuration_is_safe(None) is False
    assert runtime_configuration_is_startable(None) is False


def test_result_requires_correct_runtime_type():
    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    with pytest.raises(TypeError):
        ConfigurationRuntimeResult(
            runtime=None,
            configuration=configuration,
            startup_allowed=True,
        )


def test_result_requires_correct_configuration_type():
    runtime = create_application_runtime()

    with pytest.raises(TypeError):
        ConfigurationRuntimeResult(
            runtime=runtime,
            configuration=None,
            startup_allowed=True,
        )


def test_result_requires_boolean_startup_permission():
    runtime = create_application_runtime()

    configuration = RuntimeConfigurationState(
        configuration={},
        recovered=False,
        safe=True,
    )

    with pytest.raises(TypeError):
        ConfigurationRuntimeResult(
            runtime=runtime,
            configuration=configuration,
            startup_allowed="yes",
        )
