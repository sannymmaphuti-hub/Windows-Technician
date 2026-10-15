from dataclasses import dataclass

from engine.case_ownership import CaseOwnership
from engine.diagnostic_case import DiagnosticCase
from engine.operation_authorization_policy import OperationAuthorizationPolicy
from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import TechnicianPermission


@dataclass(frozen=True)
class CaseAccessDecision:
    technician_id: str
    case_id: str
    operation: str
    allowed: bool
    reason: str

    def projection(self):
        return {
            "technician_id": self.technician_id,
            "case_id": self.case_id,
            "operation": self.operation,
            "allowed": self.allowed,
            "reason": self.reason,
        }


class CaseAccessPolicy:
    """Evaluates case access without modifying the case or its workflow."""

    OPERATION_PERMISSIONS = {
        "VIEW_CASE": TechnicianPermission.VIEW_CASE,
        "VIEW_DIAGNOSTICS": TechnicianPermission.VIEW_DIAGNOSTICS,
        "VIEW_AUDIT_HISTORY": TechnicianPermission.VIEW_AUDIT_HISTORY,
        "ADD_CASE_NOTE": TechnicianPermission.ADD_CASE_NOTE,
        "ASSIGN_CASE": TechnicianPermission.ASSIGN_CASE,
        "HANDOFF_CASE": TechnicianPermission.HANDOFF_CASE,
    }

    def __init__(self, operation_policy=None):
        self.operation_policy = (
            operation_policy or OperationAuthorizationPolicy()
        )

    def evaluate(self, technician, case, operation, ownership=None):
        if not isinstance(technician, TechnicianIdentity):
            return CaseAccessDecision(
                "", "", str(operation), False,
                "INVALID_TECHNICIAN_IDENTITY",
            )

        if not isinstance(case, DiagnosticCase):
            return CaseAccessDecision(
                technician.technician_id, "", str(operation), False,
                "INVALID_CASE",
            )

        if not isinstance(operation, str) or not operation.strip():
            return CaseAccessDecision(
                technician.technician_id, case.case_id, str(operation),
                False, "INVALID_OPERATION",
            )

        normalized = operation.strip().upper()

        if normalized not in self.OPERATION_PERMISSIONS:
            return CaseAccessDecision(
                technician.technician_id, case.case_id, normalized,
                False, "UNSUPPORTED_CASE_OPERATION",
            )

        if not self.operation_policy.evaluate(
            technician, normalized
        ).allowed:
            return CaseAccessDecision(
                technician.technician_id, case.case_id, normalized,
                False, "PERMISSION_DENIED",
            )

        if ownership is not None:
            if not isinstance(ownership, CaseOwnership):
                return CaseAccessDecision(
                    technician.technician_id, case.case_id, normalized,
                    False, "INVALID_OWNERSHIP",
                )

            if ownership.case.case_id != case.case_id:
                return CaseAccessDecision(
                    technician.technician_id, case.case_id, normalized,
                    False, "CASE_OWNERSHIP_MISMATCH",
                )

            if ownership.owner_id != technician.technician_id:
                return CaseAccessDecision(
                    technician.technician_id, case.case_id, normalized,
                    False, "CASE_NOT_OWNED_BY_TECHNICIAN",
                )

        return CaseAccessDecision(
            technician.technician_id, case.case_id, normalized,
            True, "CASE_ACCESS_GRANTED",
        )
