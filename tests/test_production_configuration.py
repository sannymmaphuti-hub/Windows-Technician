from packaging.application_runtime import create_application_runtime
from packaging.application_runtime_configuration import (
    RuntimeConfigurationState,
)
from packaging.production_configuration import (
    ProductionConfiguration,
    ProductionConfigurationResult,
    apply_production_configuration,
    build_production_configuration,
    production_configuration_allows_startup,
    production_configuration_is_safe,
)


def test_build_production_configuration():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=True,
    )

    result = build_production_configuration(configuration)

    assert isinstance(result, ProductionConfiguration)
    assert result.state is configuration


def test_safe_configuration_allows_startup():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=True,
    )

    production = build_production_configuration(configuration)
    runtime = create_application_runtime()

    result = apply_production_configuration(
        runtime,
        production,
    )

    assert isinstance(result, ProductionConfigurationResult)
    assert result.startup_allowed is True
    assert production_configuration_allows_startup(result) is True


def test_unsafe_configuration_blocks_startup():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=False,
    )

    production = build_production_configuration(configuration)
    runtime = create_application_runtime()

    result = apply_production_configuration(
        runtime,
        production,
    )

    assert result.startup_allowed is False
    assert production_configuration_allows_startup(result) is False


def test_safe_configuration_is_reported_safe():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=True,
    )

    production = build_production_configuration(configuration)

    assert production_configuration_is_safe(production) is True


def test_unsafe_configuration_is_reported_unsafe():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=False,
    )

    production = build_production_configuration(configuration)

    assert production_configuration_is_safe(production) is False


def test_configuration_application_does_not_start_runtime():
    configuration = RuntimeConfigurationState(
        configuration={"logging": True},
        recovered=False,
        safe=True,
    )

    production = build_production_configuration(configuration)
    runtime = create_application_runtime()

    result = apply_production_configuration(
        runtime,
        production,
    )

    assert result.runtime.lifecycle.state.value == "created"

    for service in result.runtime.services.services:
        assert service.state.value == "unavailable"
