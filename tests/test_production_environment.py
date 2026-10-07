from packaging.diagnostic_dataset_environment import (
    DiagnosticDatasetEnvironment,
)
from packaging.display_environment import DisplayEnvironment
from packaging.memory_environment import MemoryEnvironment
from packaging.network_environment import (
    NetworkEnvironment,
    NetworkState,
)
from packaging.permission_environment import PermissionEnvironment
from packaging.privileged_operation import (
    PermissionContext,
    PrivilegeLevel,
)
from packaging.production_environment import (
    ProductionEnvironment,
    ProductionEnvironmentResult,
    evaluate_production_environment,
    production_environment_is_safe,
)
from packaging.service_environment import (
    ServiceEnvironment,
    ServiceState,
)
from packaging.windows_environment import WindowsEnvironment


def make_windows(version: str = "11.0") -> WindowsEnvironment:
    return WindowsEnvironment(
        operating_system="Windows",
        operating_system_version=version,
        windows_build="26200",
        architecture="AMD64",
        python_version="3.14.4",
        application_version="0.9.0",
    )


def make_environment(
    *,
    windows_version: str = "11.0",
    memory: int = 8 * 1024 * 1024 * 1024,
    width: int = 1920,
    height: int = 1080,
    dpi: int = 100,
    dataset_count: int = 100,
    service_state: ServiceState = ServiceState.RUNNING,
    network_state: NetworkState = NetworkState.AVAILABLE,
    privilege: PrivilegeLevel = PrivilegeLevel.ELEVATED,
) -> ProductionEnvironment:
    return ProductionEnvironment(
        windows=make_windows(windows_version),
        memory=MemoryEnvironment(
            total_memory_bytes=memory
        ),
        display=DisplayEnvironment(
            width_pixels=width,
            height_pixels=height,
            dpi_scale_percent=dpi,
        ),
        dataset=DiagnosticDatasetEnvironment(
            item_count=dataset_count
        ),
        service=ServiceEnvironment(
            service_name="TestService",
            state=service_state,
        ),
        network=NetworkEnvironment(
            state=network_state
        ),
        permissions=PermissionEnvironment(
            context=PermissionContext(
                privilege_level=privilege
            )
        ),
    )


def test_standard_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment()
    )

    assert result.compatible
    assert production_environment_is_safe(
        make_environment()
    )


def test_windows_10_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(windows_version="10.0")
    )

    assert result.compatible


def test_low_memory_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            memory=2 * 1024 * 1024 * 1024
        )
    )

    assert result.compatible


def test_high_memory_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            memory=32 * 1024 * 1024 * 1024
        )
    )

    assert result.compatible


def test_small_display_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            width=1024,
            height=600,
        )
    )

    assert result.compatible


def test_high_dpi_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            dpi=200,
        )
    )

    assert result.compatible


def test_empty_dataset_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(dataset_count=0)
    )

    assert result.compatible


def test_large_dataset_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(dataset_count=1_000)
    )

    assert result.compatible


def test_stress_dataset_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(dataset_count=10_000)
    )

    assert result.compatible


def test_failed_service_does_not_make_environment_incompatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            service_state=ServiceState.FAILED
        )
    )

    assert result.compatible


def test_stopped_service_does_not_make_environment_incompatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            service_state=ServiceState.STOPPED
        )
    )

    assert result.compatible


def test_network_unavailable_does_not_break_local_environment() -> None:
    result = evaluate_production_environment(
        make_environment(
            network_state=NetworkState.UNAVAILABLE
        )
    )

    assert result.compatible


def test_network_degraded_does_not_break_environment() -> None:
    result = evaluate_production_environment(
        make_environment(
            network_state=NetworkState.DEGRADED
        )
    )

    assert result.compatible


def test_standard_permissions_do_not_break_environment() -> None:
    result = evaluate_production_environment(
        make_environment(
            privilege=PrivilegeLevel.STANDARD
        )
    )

    assert result.compatible


def test_combined_constrained_environment_is_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(
            windows_version="11.0",
            memory=2 * 1024 * 1024 * 1024,
            width=1024,
            height=600,
            dpi=200,
            dataset_count=10_000,
            service_state=ServiceState.FAILED,
            network_state=NetworkState.UNAVAILABLE,
            privilege=PrivilegeLevel.STANDARD,
        )
    )

    assert result.compatible


def test_unsupported_windows_environment_is_not_compatible() -> None:
    result = evaluate_production_environment(
        make_environment(windows_version="9.0")
    )

    assert not result.compatible


def test_invalid_environment_is_rejected() -> None:
    try:
        evaluate_production_environment(None)
    except TypeError:
        return

    raise AssertionError("Expected TypeError.")


def test_result_requires_boolean() -> None:
    try:
        ProductionEnvironmentResult(
            compatible="yes",
            reason="invalid",
        )
    except TypeError:
        return

    raise AssertionError("Expected TypeError.")


def test_result_requires_reason() -> None:
    try:
        ProductionEnvironmentResult(
            compatible=True,
            reason="",
        )
    except ValueError:
        return

    raise AssertionError("Expected ValueError.")
