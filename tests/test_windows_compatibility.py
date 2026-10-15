import pytest

from packaging.windows_compatibility import (
    SUPPORTED_MAJOR_VERSIONS,
    WindowsCompatibilityResult,
    WindowsSupportLevel,
    evaluate_windows_compatibility,
    windows_compatibility_is_safe,
)
from packaging.windows_environment import WindowsEnvironment


def make_environment(major_version: int) -> WindowsEnvironment:
    return WindowsEnvironment(
        operating_system="Windows",
        operating_system_version=f"{major_version}.0",
        windows_build="26200",
        architecture="AMD64",
        python_version="3.14.4",
        application_version="1.0.0",
    )


def test_supported_versions_are_windows_10_and_11():
    assert SUPPORTED_MAJOR_VERSIONS == frozenset({10, 11})


@pytest.mark.parametrize("major_version", [10, 11])
def test_windows_10_and_11_are_supported(major_version):
    result = evaluate_windows_compatibility(
        make_environment(major_version)
    )

    assert isinstance(result, WindowsCompatibilityResult)
    assert result.supported
    assert result.support_level is WindowsSupportLevel.SUPPORTED
    assert windows_compatibility_is_safe(
        make_environment(major_version)
    )


@pytest.mark.parametrize("major_version", [7, 8, 9, 12, 13])
def test_other_major_versions_are_not_supported(major_version):
    result = evaluate_windows_compatibility(
        make_environment(major_version)
    )

    assert not result.supported
    assert result.support_level is WindowsSupportLevel.UNSUPPORTED
    assert not windows_compatibility_is_safe(
        make_environment(major_version)
    )


def test_result_requires_boolean_supported_value():
    with pytest.raises(TypeError):
        WindowsCompatibilityResult(
            supported="yes",
            support_level=WindowsSupportLevel.SUPPORTED,
            reason="invalid",
        )


def test_result_requires_valid_support_level():
    with pytest.raises(TypeError):
        WindowsCompatibilityResult(
            supported=True,
            support_level="SUPPORTED",
            reason="invalid",
        )


def test_result_requires_reason():
    with pytest.raises(ValueError):
        WindowsCompatibilityResult(
            supported=True,
            support_level=WindowsSupportLevel.SUPPORTED,
            reason="",
        )


def test_environment_type_is_required():
    with pytest.raises(TypeError):
        evaluate_windows_compatibility("Windows 11")


def test_compatibility_result_is_immutable():
    result = evaluate_windows_compatibility(
        make_environment(11)
    )

    with pytest.raises(AttributeError):
        result.supported = False
