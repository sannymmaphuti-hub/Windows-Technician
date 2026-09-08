from engine.remediation_result import RemediationResult


class RemediationExecutor:
    def execute(self, action):
        result = RemediationResult(
            action_id=action.action_id,
        )

        action.execute()

        result.execution_status = action.execution_status

        return result