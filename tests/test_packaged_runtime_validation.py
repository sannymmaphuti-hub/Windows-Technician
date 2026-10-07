"""Tests for packaged Windows Technician runtime validation."""

from pathlib import Path

from packaging.packaged_runtime_validation import (
    PackagedRuntimeValidationResult,
    validate_packaged_runtime,
)


def test_packaged_runtime_validation_result_is_immutable():
    result = PackagedRuntimeValidationResult(
        started=True,
        survived_startup=True,
        terminated=True,
        return_code=0,
        executable=Path("WindowsTechnician.exe"),
    )

    try:
        result.started = False
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "PackagedRuntimeValidationResult must be immutable."
        )


def test_packaged_runtime_smoke_test():
    result = validate_packaged_runtime()

    assert result.started is True
    assert result.survived_startup is True
    assert result.terminated is True
    assert result.errors == ()


def test_packaged_runtime_points_to_windows_executable():
    result = validate_packaged_runtime()

    assert result.executable.name == "WindowsTechnician.exe"
    assert result.executable.parent.name == "WindowsTechnician"
