# ==========================================
# Windows Technician v0.5
# REMEDIATION ELIGIBILITY
# ==========================================

from engine.remediation_action import RemediationAction


class RemediationEligibility:

    def is_eligible(self, action):
        if not isinstance(action, RemediationAction):
            return False

        if action.operation is None:
            return False

        if (
            action.requires_authorization
            and action.authorization_status != "AUTHORIZED"
        ):
            return False

        if action.execution_status in {
            "FAILED",
            "EXECUTED",
        }:
            return False

        return True

    def get_reason(self, action):
        if not isinstance(action, RemediationAction):
            return "INVALID_ACTION"

        if action.authorization_status == "DENIED":
            return "DENIED"

        if action.authorization_status != "AUTHORIZED":
            return "NOT_AUTHORIZED"

        if action.operation is None:
            return "OPERATION_NOT_BOUND"

        if action.execution_status == "FAILED":
            return "ALREADY_FAILED"

        if action.execution_status == "EXECUTED":
            return "ALREADY_EXECUTED"

        return "ELIGIBLE"
