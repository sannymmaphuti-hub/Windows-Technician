from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import (
    TechnicianPermission,
    TechnicianPermissions,
)


class TechnicianRolePolicy:
    """Maps recognized technician roles to explicit permission sets."""

    ROLE_PERMISSIONS = {
        "TECHNICIAN": frozenset({
            TechnicianPermission.VIEW_CASE,
            TechnicianPermission.VIEW_DIAGNOSTICS,
            TechnicianPermission.ADD_CASE_NOTE,
            TechnicianPermission.HANDOFF_CASE,
        }),
        "SENIOR_TECHNICIAN": frozenset({
            TechnicianPermission.VIEW_CASE,
            TechnicianPermission.VIEW_DIAGNOSTICS,
            TechnicianPermission.VIEW_AUDIT_HISTORY,
            TechnicianPermission.ADD_CASE_NOTE,
            TechnicianPermission.ASSIGN_CASE,
            TechnicianPermission.HANDOFF_CASE,
        }),
        "SUPERVISOR": frozenset({
            TechnicianPermission.VIEW_CASE,
            TechnicianPermission.VIEW_DIAGNOSTICS,
            TechnicianPermission.VIEW_AUDIT_HISTORY,
            TechnicianPermission.ADD_CASE_NOTE,
            TechnicianPermission.ASSIGN_CASE,
            TechnicianPermission.HANDOFF_CASE,
        }),
        "ADMINISTRATOR": frozenset({
            TechnicianPermission.VIEW_CASE,
            TechnicianPermission.VIEW_DIAGNOSTICS,
            TechnicianPermission.VIEW_AUDIT_HISTORY,
            TechnicianPermission.ADD_CASE_NOTE,
            TechnicianPermission.ASSIGN_CASE,
            TechnicianPermission.HANDOFF_CASE,
            TechnicianPermission.MANAGE_TECHNICIANS,
            TechnicianPermission.MANAGE_SECURITY_POLICY,
        }),
    }

    def __init__(self):
        self._policies = dict(self.ROLE_PERMISSIONS)

    def permissions_for(self, technician):
        if not isinstance(technician, TechnicianIdentity):
            raise TypeError("technician must be a TechnicianIdentity.")

        permissions = self._policies.get(technician.role, frozenset())
        return TechnicianPermissions(permissions)

    def allows(self, technician, permission):
        return self.permissions_for(technician).allows(permission)

    def projection(self):
        return {
            role: sorted(permission.value for permission in permissions)
            for role, permissions in sorted(self._policies.items())
        }
