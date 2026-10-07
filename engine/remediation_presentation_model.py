from copy import deepcopy


class RemediationPresentationModel:
    """
    Read-only presentation model for an existing remediation action.

    This model explains an already-created remediation action to the
    user. It does not authorize, execute, retry, verify, or modify
    remediation state.
    """

    AUTHORIZATION_STATES = {
        "UNAUTHORIZED",
        "AUTHORIZED",
        "DENIED",
    }

    EXECUTION_STATES = {
        "NOT_EXECUTED",
        "EXECUTED",
        "FAILED",
    }

    def __init__(self, action):
        if not isinstance(action, dict):
            raise ValueError("action must be a dictionary.")

        self._action = deepcopy(action)

    @staticmethod
    def _first_value(data, *keys, default=None):
        for key in keys:
            value = data.get(key)
            if value is not None and value != "":
                return value
        return default

    def action_id(self):
        value = self._first_value(
            self._action,
            "action_id",
            "id",
            "uuid",
            default=None,
        )
        return None if value is None else str(value)

    def action_type(self):
        value = self._first_value(
            self._action,
            "action_type",
            "type",
            "name",
            "action",
            default="UNKNOWN",
        )
        return str(value)

    def title(self):
        value = self._first_value(
            self._action,
            "title",
            "name",
            "summary",
            default=self.action_type(),
        )
        return str(value)

    def explanation(self):
        value = self._first_value(
            self._action,
            "explanation",
            "description",
            "reason",
            "message",
            default="No explanation available.",
        )
        return str(value)

    def risk(self):
        value = self._first_value(
            self._action,
            "risk",
            "risk_level",
            "severity",
            default="UNKNOWN",
        )
        return str(value).upper()

    def authorization_status(self):
        value = self._first_value(
            self._action,
            "authorization_status",
            "authorization",
            "auth_status",
            "status",
            default="UNAUTHORIZED",
        )
        value = str(value).upper()

        if value not in self.AUTHORIZATION_STATES:
            return "UNAUTHORIZED"

        return value

    def execution_status(self):
        value = self._first_value(
            self._action,
            "execution_status",
            "execution",
            "execution_state",
            default="NOT_EXECUTED",
        )
        value = str(value).upper()

        if value not in self.EXECUTION_STATES:
            return "NOT_EXECUTED"

        return value

    def is_authorized(self):
        return self.authorization_status() == "AUTHORIZED"

    def has_executed(self):
        return self.execution_status() == "EXECUTED"

    def requires_authorization(self):
        return not self.is_authorized()

    def user_message(self):
        authorization = self.authorization_status()
        execution = self.execution_status()

        if execution == "EXECUTED":
            return "This remediation has already been executed."

        if execution == "FAILED":
            return "This remediation was attempted but failed."

        if authorization == "DENIED":
            return "This remediation has been denied and will not be executed."

        if authorization == "AUTHORIZED":
            return "This remediation has been authorized and is ready for the existing execution workflow."

        return "This remediation requires your authorization before it can be executed."

    def to_dict(self):
        return {
            "action_id": self.action_id(),
            "action_type": self.action_type(),
            "title": self.title(),
            "explanation": self.explanation(),
            "risk": self.risk(),
            "authorization_status": self.authorization_status(),
            "execution_status": self.execution_status(),
            "is_authorized": self.is_authorized(),
            "has_executed": self.has_executed(),
            "requires_authorization": self.requires_authorization(),
            "user_message": self.user_message(),
        }
