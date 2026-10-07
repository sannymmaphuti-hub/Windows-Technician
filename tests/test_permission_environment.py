import pytest

from packaging.permission_environment import (
    PermissionCompatibilityResult,
    PermissionEnvironment,
    PermissionEnvironmentLevel,
    classify_permission_environment,
    evaluate_permission_compatibility,
    operation_is_allowed_in_environment,
    permission_compatibility_is_safe,
)
from packaging.privileged_operation import (
    OperationPrivilege,
    PermissionContext,
    PrivilegeLevel,
)


def make_context(
    privilege: PrivilegeLevel,
) -> PermissionContext:
    return PermissionContext(
        privilege_level=privilege,
    )


def make_environment(
    privilege: PrivilegeLevel,
) -> PermissionEnvironment:
    return PermissionEnvironment(
        context=make_context(privilege),
    )


def test_standard_permission_is_classified() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    assert (
        classify_permission_environment(environment)
        is PermissionEnvironmentLevel.STANDARD
    )


def test_elevated_permission_is_classified() -> None:
    environment = make_environment(PrivilegeLevel.ELEVATED)

    assert (
        classify_permission_environment(environment)
        is PermissionEnvironmentLevel.ELEVATED
    )


@pytest.mark.parametrize(
    "privilege",
    [
        PrivilegeLevel.STANDARD,
        PrivilegeLevel.ELEVATED,
    ],
)
def test_known_permission_environments_are_compatible(
    privilege: PrivilegeLevel,
) -> None:
    environment = make_environment(privilege)

    result = evaluate_permission_compatibility(environment)

    assert result.compatible
    assert permission_compatibility_is_safe(environment)


def test_standard_environment_allows_standard_operation() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    assert operation_is_allowed_in_environment(
        environment,
        operation_id="diagnostic.read",
        required_privilege=OperationPrivilege.STANDARD,
    )


def test_standard_environment_blocks_elevated_operation() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    assert not operation_is_allowed_in_environment(
        environment,
        operation_id="service.restart",
        required_privilege=OperationPrivilege.ELEVATED,
    )


def test_elevated_environment_allows_standard_operation() -> None:
    environment = make_environment(PrivilegeLevel.ELEVATED)

    assert operation_is_allowed_in_environment(
        environment,
        operation_id="diagnostic.read",
        required_privilege=OperationPrivilege.STANDARD,
    )


def test_elevated_environment_allows_elevated_operation() -> None:
    environment = make_environment(PrivilegeLevel.ELEVATED)

    assert operation_is_allowed_in_environment(
        environment,
        operation_id="service.restart",
        required_privilege=OperationPrivilege.ELEVATED,
    )


def test_standard_permissions_keep_diagnostics_available() -> None:
    result = evaluate_permission_compatibility(
        make_environment(PrivilegeLevel.STANDARD)
    )

    assert result.compatible
    assert "diagnostics" in result.reason.lower()


def test_standard_permissions_do_not_implicitly_elevate() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    assert not operation_is_allowed_in_environment(
        environment,
        operation_id="privileged.diagnostic",
        required_privilege=OperationPrivilege.ELEVATED,
    )


def test_empty_operation_id_is_rejected() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    with pytest.raises(ValueError):
        operation_is_allowed_in_environment(
            environment,
            operation_id="",
            required_privilege=OperationPrivilege.STANDARD,
        )


def test_whitespace_operation_id_is_rejected() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    with pytest.raises(ValueError):
        operation_is_allowed_in_environment(
            environment,
            operation_id="   ",
            required_privilege=OperationPrivilege.STANDARD,
        )


def test_invalid_environment_is_rejected() -> None:
    with pytest.raises(TypeError):
        classify_permission_environment(None)


def test_invalid_evaluation_environment_is_rejected() -> None:
    with pytest.raises(TypeError):
        evaluate_permission_compatibility(None)


def test_invalid_operation_environment_is_rejected() -> None:
    with pytest.raises(TypeError):
        operation_is_allowed_in_environment(
            None,
            operation_id="diagnostic.read",
            required_privilege=OperationPrivilege.STANDARD,
        )


def test_invalid_required_privilege_is_rejected() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    with pytest.raises(TypeError):
        operation_is_allowed_in_environment(
            environment,
            operation_id="diagnostic.read",
            required_privilege="STANDARD",
        )


def test_invalid_permission_context_is_rejected() -> None:
    with pytest.raises(TypeError):
        PermissionEnvironment(context="invalid")


def test_result_requires_boolean_compatibility() -> None:
    with pytest.raises(TypeError):
        PermissionCompatibilityResult(
            compatible="yes",
            level=PermissionEnvironmentLevel.STANDARD,
            reason="invalid",
        )


def test_result_requires_valid_level() -> None:
    with pytest.raises(TypeError):
        PermissionCompatibilityResult(
            compatible=True,
            level="STANDARD",
            reason="invalid",
        )


def test_result_requires_reason() -> None:
    with pytest.raises(ValueError):
        PermissionCompatibilityResult(
            compatible=True,
            level=PermissionEnvironmentLevel.STANDARD,
            reason="",
        )


def test_permission_environment_is_immutable() -> None:
    environment = make_environment(PrivilegeLevel.STANDARD)

    with pytest.raises(AttributeError):
        environment.context = make_context(
            PrivilegeLevel.ELEVATED
        )


def test_permission_result_is_immutable() -> None:
    result = evaluate_permission_compatibility(
        make_environment(PrivilegeLevel.STANDARD)
    )

    with pytest.raises(AttributeError):
        result.compatible = False
