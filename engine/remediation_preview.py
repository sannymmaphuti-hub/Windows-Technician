from engine.remediation_action import RemediationAction


class RemediationPreview:
    """Provide a read-only preview of a remediation action."""

    def __init__(self, action):
        if not isinstance(action, RemediationAction):
            raise ValueError(
                "RemediationPreview requires a RemediationAction."
            )

        self.action = action

    @property
    def action_id(self):
        return self.action.action_id

    @property
    def description(self):
        return self.action.description

    @property
    def authorization_status(self):
        return self.action.authorization_status

    @property
    def requires_authorization(self):
        return self.action.requires_authorization