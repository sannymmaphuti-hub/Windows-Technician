from engine.remediation_executor import RemediationExecutor
from engine.remediation_verifier import RemediationVerifier
from engine.remediation_audit import RemediationAudit


class RemediationCoordinator:

    def __init__(self):
        self.executor = RemediationExecutor()
        self.verifier = RemediationVerifier()
        self.audit = RemediationAudit()

    def execute(self, action, expected=None, observed=None):
        result = self.executor.execute(action)

        if (
            result.execution_status == "EXECUTED"
            and expected is not None
            and observed is not None
        ):
            result.verification_result = self.verifier.verify(
                expected=expected,
                observed=observed,
                action_id=action.action_id,
            )

        self.audit.record(
            action_id=result.action_id,
            execution_status=result.execution_status,
            reason=result.reason,
            verification_result=result.verification_result,
        )

        return result
