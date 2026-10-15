from copy import deepcopy

from engine.case_access_policy import CaseAccessDecision
from engine.operation_authorization_policy import (
    OperationAuthorizationDecision,
)
from engine.security_audit_history import SecurityAuditHistory


class SecurityDecisionProjection:
    """Read-only reporting surface for security decisions and audit history."""

    def __init__(
        self,
        audit_history,
        operation_decisions=(),
        case_access_decisions=(),
    ):
        if not isinstance(audit_history, SecurityAuditHistory):
            raise TypeError(
                "audit_history must be a SecurityAuditHistory."
            )

        self.audit_history = audit_history
        self._operation_decisions = self._validate_decisions(
            operation_decisions,
            OperationAuthorizationDecision,
            "operation_decisions",
        )
        self._case_access_decisions = self._validate_decisions(
            case_access_decisions,
            CaseAccessDecision,
            "case_access_decisions",
        )

    @staticmethod
    def _validate_decisions(decisions, expected_type, name):
        try:
            result = tuple(decisions)
        except TypeError as exc:
            raise TypeError(f"{name} must be an iterable.") from exc

        if not all(isinstance(item, expected_type) for item in result):
            raise TypeError(
                f"Every {name} entry must be a "
                f"{expected_type.__name__}."
            )

        return result

    def projection(self):
        return deepcopy({
            "operation_decisions": [
                decision.projection()
                for decision in self._operation_decisions
            ],
            "case_access_decisions": [
                decision.projection()
                for decision in self._case_access_decisions
            ],
            "audit_history": self.audit_history.projection(),
            "summary": {
                "operation_decision_count": len(
                    self._operation_decisions
                ),
                "case_access_decision_count": len(
                    self._case_access_decisions
                ),
                "audit_event_count": self.audit_history.event_count,
                "operation_denials": sum(
                    not decision.allowed
                    for decision in self._operation_decisions
                ),
                "case_access_denials": sum(
                    not decision.allowed
                    for decision in self._case_access_decisions
                ),
            },
        })

    def __repr__(self):
        return (
            "SecurityDecisionProjection("
            f"operation_decisions={len(self._operation_decisions)}, "
            f"case_access_decisions={len(self._case_access_decisions)}, "
            f"audit_events={self.audit_history.event_count})"
        )
