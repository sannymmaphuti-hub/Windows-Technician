from engine.remediation_executor import RemediationExecutor
from engine.remediation_verifier import RemediationVerifier


class RemediationCoordinator:
    def __init__(self):
        self.executor = RemediationExecutor()
        self.verifier = RemediationVerifier()

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

        return result