# ==========================================
# Windows Technician v0.5
# REMEDIATION OPERATION
# ==========================================


class RemediationOperation:

    def __init__(
        self,
        operation_id,
        description,
        handler=None,
    ):
        if operation_id is None:
            raise ValueError("operation_id is required")

        if description is None:
            raise ValueError("description is required")

        if handler is not None and not callable(handler):
            raise ValueError("handler must be callable")

        self.operation_id = operation_id
        self.description = description
        self.handler = handler

        self.execution_status = "NOT_EXECUTED"
