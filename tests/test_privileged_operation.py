"""Tests for the production privileged-operation security boundary."""

import pytest

from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegeLevel,
    PrivilegedOperation,
    operation_requires_elevation,
    privilege_allows_operation,
    privileged_operation_is_safe_to_execute,
)


def test_standard_operation_does_not_require_elevation():
    operation = PrivilegedOperation(
        operation_id="diagnostic-read",
        required_privilege=OperationPrivilege.STANDARD,
    )

    assert not operation_requires_elevation(operation)


def test_elevated_operation_requires_elevation():
    operation = PrivilegedOperation(
        operation_id="service-repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )

    assert operation_requires_elevation(operation)


def test_standard_operation_allowed_for_standard_context():
    operation = PrivilegedOperation(
        operation_id="diagnostic-read",
        required_privilege=OperationPrivilege.STANDARD,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert privilege_allows_operation(operation, context)


def test_standard_operation_allowed_for_elevated_context():
    operation = PrivilegedOperation(
        operation_id="diagnostic-read",
        required_privilege=OperationPrivilege.STANDARD,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED,
    )

    assert privilege_allows_operation(operation, context)


def test_elevated_operation_rejected_for_standard_context():
    operation = PrivilegedOperation(
        operation_id="service-repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert not privilege_allows_operation(operation, context)


def test_elevated_operation_allowed_for_elevated_context():
    operation = PrivilegedOperation(
        operation_id="service-repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED,
    )

    assert privilege_allows_operation(operation, context)


def test_final_safety_boundary_matches_privilege_decision():
    operation = PrivilegedOperation(
        operation_id="service-repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED,
    )

    assert privileged_operation_is_safe_to_execute(
        operation,
        context,
    )


@pytest.mark.parametrize(
    "operation_id",
    [
        "",
        "   ",
    ],
)
def test_empty_operation_id_is_rejected(operation_id):
    with pytest.raises(ValueError):
        PrivilegedOperation(
            operation_id=operation_id,
            required_privilege=OperationPrivilege.STANDARD,
        )


def test_invalid_operation_privilege_is_rejected():
    with pytest.raises(TypeError):
        PrivilegedOperation(
            operation_id="operation",
            required_privilege="ELEVATED",
        )


def test_invalid_privilege_context_is_rejected():
    with pytest.raises(TypeError):
        PermissionContext(
            privilege_level="ELEVATED",
        )


def test_operation_requires_elevation_rejects_wrong_type():
    with pytest.raises(TypeError):
        operation_requires_elevation(object())


def test_privilege_allows_operation_rejects_wrong_operation_type():
    context = PermissionContext(
        privilege_level=PrivilegeLevel.ELEVATED,
    )

    with pytest.raises(TypeError):
        privilege_allows_operation(
            object(),
            context,
        )


def test_privilege_allows_operation_rejects_wrong_context_type():
    operation = PrivilegedOperation(
        operation_id="operation",
        required_privilege=OperationPrivilege.STANDARD,
    )

    with pytest.raises(TypeError):
        privilege_allows_operation(
            operation,
            object(),
        )


def test_final_boundary_rejects_standard_context_for_elevated_operation():
    operation = PrivilegedOperation(
        operation_id="service-repair",
        required_privilege=OperationPrivilege.ELEVATED,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert not privileged_operation_is_safe_to_execute(
        operation,
        context,
    )


def test_final_boundary_allows_standard_operation_without_elevation():
    operation = PrivilegedOperation(
        operation_id="diagnostic-read",
        required_privilege=OperationPrivilege.STANDARD,
    )
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    assert privileged_operation_is_safe_to_execute(
        operation,
        context,
    )


def test_privilege_levels_are_distinct():
    assert PrivilegeLevel.STANDARD != PrivilegeLevel.ELEVATED


def test_operation_privilege_levels_are_distinct():
    assert OperationPrivilege.STANDARD != OperationPrivilege.ELEVATED


def test_permission_context_is_immutable():
    context = PermissionContext(
        privilege_level=PrivilegeLevel.STANDARD,
    )

    with pytest.raises(AttributeError):
        context.privilege_level = PrivilegeLevel.ELEVATED


def test_privileged_operation_is_immutable():
    operation = PrivilegedOperation(
        operation_id="operation",
        required_privilege=OperationPrivilege.STANDARD,
    )

    with pytest.raises(AttributeError):
        operation.operation_id = "changed"
