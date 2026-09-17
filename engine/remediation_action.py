# ==========================================
# Windows Technician v0.5
# REMEDIATION ACTION
# ==========================================


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
        self.category = category
        self.severity = severity

        self.authorization_status = "UNAUTHORIZED"
        self.execution_status = "NOT_EXECUTED"
        self.failure_reason = None
        self._operation = operation

    @property
    def operation(self):
        return self._operation

    @operation.setter
    def operation(self, operation):
        if self.execution_status in {"EXECUTED", "FAILED"}:
            return

        self._operation = operation

    def authorize(self):
        if self.authorization_status == "DENIED":
            return

        if self.execution_status in {"EXECUTED", "FAILED"}:
            return

        self.authorization_status = "AUTHORIZED"

    def deny(self):
        if self.execution_status in {"EXECUTED", "FAILED"}:
            return

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
        except Exception as error:
            self.execution_status = "FAILED"

            if hasattr(self.operation, "execution_status"):
                self.operation.execution_status = "FAILED"

            self.failure_reason = str(error)

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
