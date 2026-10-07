"""Tests for runtime dependency availability."""

import pytest

from packaging.dependency_boundary import (
    DependencyStatus,
    all_dependencies_available,
    check_dependencies,
    check_dependency,
)


def test_available_dependency_is_detected():
    result = check_dependency("json")

    assert result.available is True
    assert result.name == "json"
    assert result.error_type is None
    assert result.message is None


def test_missing_dependency_is_contained():
    result = check_dependency(
        "windows_technician_dependency_that_does_not_exist"
    )

    assert result.available is False
    assert result.error_type is not None
    assert result.message is not None


def test_missing_dependency_does_not_escape_boundary():
    result = check_dependency(
        "another_missing_windows_technician_dependency"
    )

    assert result.available is False


def test_dependency_name_is_required():
    with pytest.raises(ValueError):
        check_dependency("")


def test_dependency_status_requires_name():
    with pytest.raises(ValueError):
        DependencyStatus(
            name="",
            available=True,
        )


def test_available_dependency_cannot_have_error_details():
    with pytest.raises(ValueError):
        DependencyStatus(
            name="json",
            available=True,
            error_type="RuntimeError",
        )


def test_unavailable_dependency_requires_error_type():
    with pytest.raises(ValueError):
        DependencyStatus(
            name="missing",
            available=False,
        )


def test_multiple_dependencies_are_checked():
    results = check_dependencies(
        ("json", "pathlib"),
    )

    assert len(results) == 2
    assert all(result.available for result in results)


def test_multiple_dependencies_preserve_order():
    results = check_dependencies(
        ("json", "pathlib"),
    )

    assert results[0].name == "json"
    assert results[1].name == "pathlib"


def test_dependency_collection_requires_tuple():
    with pytest.raises(TypeError):
        check_dependencies(["json"])


def test_all_dependencies_available_when_all_pass():
    results = check_dependencies(
        ("json", "pathlib"),
    )

    assert all_dependencies_available(results) is True


def test_all_dependencies_unavailable_when_one_fails():
    results = (
        DependencyStatus(
            name="json",
            available=True,
        ),
        DependencyStatus(
            name="missing",
            available=False,
            error_type="ModuleNotFoundError",
            message="missing",
        ),
    )

    assert all_dependencies_available(results) is False


def test_dependency_status_is_immutable():
    result = check_dependency("json")

    with pytest.raises(AttributeError):
        result.available = False
