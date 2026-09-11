from engine.remediation_result import RemediationResult
from engine.remediation_eligibility import RemediationEligibility


class RemediationExecutor:

    def __init__(self, eligibility=None):
        self.eligibility = eligibility or RemediationEligibility()

    def execute(self, action):
        if getattr(action, "execution_status", None) in {
            "EXECUTED",
            "FAILED",
        }:
            result = RemediationResult(
                action_id=getattr(action, "action_id", None)
            )
            result.execution_status = action.execution_status
            return result

        if not self.eligibility.is_eligible(action):
            action_id = getattr(action, "action_id", None)
            result = RemediationResult(action_id=action_id)

            get_reason = getattr(
                self.eligibility,
                "get_reason",
                None,
            )

            if get_reason is not None:
                result.reason = get_reason(action)

            return result

        result = RemediationResult(action_id=action.action_id)

        action.execute()
        result.execution_status = action.execution_status

        if action.execution_status == "FAILED":
            result.reason = getattr(action, "failure_reason", None)

        return result