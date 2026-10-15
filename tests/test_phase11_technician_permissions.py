import pytest

from engine.technician_permissions import (
    TechnicianPermission,
    TechnicianPermissions,
)


def test_permissions_default_to_empty():
    permissions = TechnicianPermissions()

    assert permissions.permissions == frozenset()
    assert permissions.projection() == {"permissions": []}


def test_explicit_permissions_are_granted():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
        TechnicianPermission.ADD_CASE_NOTE,
    ])

    assert permissions.allows(TechnicianPermission.VIEW_CASE)
    assert permissions.allows("ADD_CASE_NOTE")
    assert not permissions.allows(TechnicianPermission.EXECUTE_REMEDIATION)


def test_string_permissions_are_supported():
    permissions = TechnicianPermissions(["VIEW_CASE"])

    assert permissions.allows(TechnicianPermission.VIEW_CASE)


def test_duplicate_permissions_are_deduplicated():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
        TechnicianPermission.VIEW_CASE,
    ])

    assert len(permissions.permissions) == 1


def test_permission_collection_is_immutable():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
    ])

    assert isinstance(permissions.permissions, frozenset)


def test_unknown_permission_is_rejected_during_construction():
    with pytest.raises(ValueError, match="Unsupported technician permission"):
        TechnicianPermissions(["DELETE_ALL_DATA"])


def test_invalid_permission_type_is_rejected():
    with pytest.raises(TypeError):
        TechnicianPermissions([123])


def test_unknown_permission_check_fails_closed():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
    ])

    assert not permissions.allows("DELETE_ALL_DATA")
    assert not permissions.allows(None)


def test_projection_is_defensive():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
    ])

    first = permissions.projection()
    first["permissions"].append("EXECUTE_REMEDIATION")

    assert permissions.projection() == {
        "permissions": ["VIEW_CASE"],
    }


def test_repr_does_not_expose_permission_details():
    permissions = TechnicianPermissions([
        TechnicianPermission.VIEW_CASE,
    ])

    assert repr(permissions) == "TechnicianPermissions(count=1)"
