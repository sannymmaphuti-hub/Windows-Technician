from enum import Enum


class TechnicianPermission(str, Enum):
    VIEW_CASE = "VIEW_CASE"
    VIEW_DIAGNOSTICS = "VIEW_DIAGNOSTICS"
    VIEW_AUDIT_HISTORY = "VIEW_AUDIT_HISTORY"
    ADD_CASE_NOTE = "ADD_CASE_NOTE"
    ASSIGN_CASE = "ASSIGN_CASE"
    HANDOFF_CASE = "HANDOFF_CASE"
    AUTHORIZE_REMEDIATION = "AUTHORIZE_REMEDIATION"
    EXECUTE_REMEDIATION = "EXECUTE_REMEDIATION"
    MANAGE_TECHNICIANS = "MANAGE_TECHNICIANS"
    MANAGE_SECURITY_POLICY = "MANAGE_SECURITY_POLICY"


class TechnicianPermissions:
    """Explicit, immutable set of permissions granted to a technician."""

    def __init__(self, permissions=()):
        normalized = set()

        for permission in permissions:
            if isinstance(permission, TechnicianPermission):
                normalized.add(permission)
                continue

            if isinstance(permission, str):
                try:
                    normalized.add(TechnicianPermission(permission))
                except ValueError as exc:
                    raise ValueError(
                        f"Unsupported technician permission: {permission!r}"
                    ) from exc
                continue

            raise TypeError(
                "Permissions must be TechnicianPermission values or valid strings."
            )

        self._permissions = frozenset(normalized)

    @property
    def permissions(self):
        return self._permissions

    def allows(self, permission):
        if isinstance(permission, str):
            try:
                permission = TechnicianPermission(permission)
            except ValueError:
                return False

        if not isinstance(permission, TechnicianPermission):
            return False

        return permission in self._permissions

    def projection(self):
        return {
            "permissions": sorted(
                permission.value for permission in self._permissions
            )
        }

    def __repr__(self):
        return f"TechnicianPermissions(count={len(self._permissions)})"
