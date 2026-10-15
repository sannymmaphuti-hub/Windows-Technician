from dataclasses import dataclass

from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import TechnicianPermission
from engine.technician_role_policy import TechnicianRolePolicy


@dataclass(frozen=True)
class OperationAuthorizationDecision:
    technician_id: str
    operation: str
    allowed: bool
    reason: str

    def projection(self):
        return {
            "technician_id": self.technician_id,
            "operation": self.operation,
            "allowed": self.allowed,
            "reason": self.reason,
        }


class OperationAuthorizationPolicy:
    """Decides whether a technician's role permits a named operation.

    This policy does not authorize a specific remediation action, grant
    consent, or execute an operation. Those remain separate boundaries.
    """

    OPERATION_PERMISSIONS = {
        "VIEW_CASE": TechnicianPermission.VIEW_CASE,
        "VIEW_DIAGNOSTICS": TechnicianPermission.VIEW_DIAGNOSTICS,
        "VIEW_AUDIT_HISTORY": TechnicianPermission.VIEW_AUDIT_HISTORY,
        "ADD_CASE_NOTE": TechnicianPermission.ADD_CASE_NOTE,
        "ASSIGN_CASE": TechnicianPermission.ASSIGN_CASE,
        "HANDOFF_CASE": TechnicianPermission.HANDOFF_CASE,
        "MANAGE_TECHNICIANS": TechnicianPermission.MANAGE_TECHNICIANS,
        "MANAGE_SECURITY_POLICY": TechnicianPermission.MANAGE_SECURITY_POLICY,
        "AUTHORIZE_REMEDIATION": TechnicianPermission.AUTHORIZE_REMEDIATION,
        "EXECUTE_REMEDIATION": TechnicianPermission.EXECUTE_REMEDIATION,
    }

    def __init__(self, role_policy=None):
        self.role_policy = role_policy or TechnicianRolePolicy()

    def evaluate(self, technician, operation):
        if not isinstance(technician, TechnicianIdentity):
            return OperationAuthorizationDecision(
                technician_id="",
                operation=str(operation),
                allowed=False,
                reason="INVALID_TECHNICIAN_IDENTITY",
            )

        if not isinstance(operation, str) or not operation.strip():
            return OperationAuthorizationDecision(
                technician_id=technician.technician_id,
                operation=str(operation),
                allowed=False,
                reason="INVALID_OPERATION",
            )

        normalized_operation = operation.strip().upper()
        permission = self.OPERATION_PERMISSIONS.get(normalized_operation)

        if permission is None:
            return OperationAuthorizationDecision(
                technician_id=technician.technician_id,
                operation=normalized_operation,
                allowed=False,
                reason="UNSUPPORTED_OPERATION",
            )

        if not self.role_policy.allows(technician, permission):
            return OperationAuthorizationDecision(
                technician_id=technician.technician_id,
                operation=normalized_operation,
                allowed=False,
                reason="PERMISSION_DENIED",
            )

        return OperationAuthorizationDecision(
            technician_id=technician.technician_id,
            operation=normalized_operation,
            allowed=True,
            reason="ROLE_PERMISSION_GRANTED",
        )
