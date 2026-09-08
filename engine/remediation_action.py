class RemediationAction:
    def __init__(
        self,
        action_id,
        description,
        requires_authorization=True,
        operation=None,
        category=None,
        severity=None,
    ):
        self.action_id = action_id
        self.description = description
        self.requires_authorization = requires_authorization
        self.operation = operation
        self.category = category
        self.severity = severity

        self.authorization_status = "UNAUTHORIZED"
        self.execution_status = "NOT_EXECUTED"

    def authorize(self):
        self.authorization_status = "AUTHORIZED"

    def deny(self):
        self.authorization_status = "DENIED"

    def execute(self):
        if self.execution_status in {"EXECUTED", "FAILED"}:
            return False

        if (
            self.requires_authorization
            and self.authorization_status != "AUTHORIZED"
        ):
            return False

        if self.operation is None:
            return False

        try:
            if hasattr(self.operation, "handler"):
                if self.operation.handler is None:
                    return False

                self.operation.handler()
            else:
                self.operation()
        except Exception:
            self.execution_status = "FAILED"

            if hasattr(self.operation, "execution_status"):
                self.operation.execution_status = "FAILED"

            return False

        self.execution_status = "EXECUTED"

        if hasattr(self.operation, "execution_status"):
            self.operation.execution_status = "EXECUTED"

        return True
    def __eq__(self, other):
        if not isinstance(other, RemediationAction):
            return NotImplemented

        return (
            self.action_id == other.action_id
            and self.description == other.description
            and self.requires_authorization
            == other.requires_authorization
            and self.category == other.category
            and self.severity == other.severity
            and self.authorization_status
            == other.authorization_status
            and self.execution_status
            == other.execution_status
        )