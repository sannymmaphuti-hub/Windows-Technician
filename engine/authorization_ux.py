from engine.remediation_action import RemediationAction


class AuthorizationUX:
    """Expose remediation authorization state for user-facing UX."""

    def __init__(self, action):
        if not isinstance(action, RemediationAction):
            raise ValueError(
                "AuthorizationUX requires a RemediationAction."
            )

        self.action = action

    @property
    def action_id(self):
        return self.action.action_id

    @property
    def description(self):
        return self.action.description

    @property
    def status(self):
        return self.action.authorization_status

    @property
    def message(self):
        messages = {
            "UNAUTHORIZED": (
                "This action requires your authorization "
                "before it can be performed."
            ),
            "AUTHORIZED": (
                "This action has been authorized."
            ),
            "DENIED": (
                "This action has been denied."
            ),
        }

        return messages.get(
            self.status,
            "The authorization status is unknown.",
        )