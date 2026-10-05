from engine.remediation_action import RemediationAction


class StatusCommunication:
    """Communicate remediation execution status without changing it."""

    def __init__(self, action):
        if not isinstance(action, RemediationAction):
            raise ValueError(
                "StatusCommunication requires a RemediationAction."
            )

        self.action = action

    @property
    def execution_status(self):
        return self.action.execution_status

    @property
    def message(self):
        messages = {
            "NOT_EXECUTED": (
                "This action has not been executed."
            ),
            "EXECUTED": (
                "This action was executed successfully. "
                "Verification is still required."
            ),
            "FAILED": (
                "This action could not be completed."
            ),
        }

        return messages.get(
            self.execution_status,
            "The action has an unknown execution status.",
        )