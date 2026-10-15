# ==========================================
# Windows Technician V1.0
# REMOTE OPERATION
# ==========================================


class RemoteOperation:

    VALID_STATES = {
        "PENDING",
        "RUNNING",
        "COMPLETED",
        "FAILED",
    }

    VALID_TYPES = {
        "DIAGNOSTIC",
    }

    def __init__(
        self,
        operation_id,
        machine_id,
        session_id,
        operation_type="DIAGNOSTIC",
    ):
        if operation_id is None:
            raise ValueError(
                "operation_id is required"
            )

        if machine_id is None:
            raise ValueError(
                "machine_id is required"
            )

        if session_id is None:
            raise ValueError(
                "session_id is required"
            )

        normalized_type = (
            operation_type.strip().upper()
            if isinstance(operation_type, str)
            else None
        )

        if normalized_type not in self.VALID_TYPES:
            raise ValueError(
                "unsupported remote operation type"
            )

        self.operation_id = operation_id
        self.machine_id = machine_id
        self.session_id = session_id
        self.operation_type = normalized_type

        self.state = "PENDING"
        self.failure = None

    def start(self):
        if self.state != "PENDING":
            raise ValueError(
                "remote operation can only start from PENDING"
            )

        self.state = "RUNNING"

    def complete(self):
        if self.state != "RUNNING":
            raise ValueError(
                "remote operation can only complete from RUNNING"
            )

        self.state = "COMPLETED"

    def fail(self, reason):
        if reason is None:
            raise ValueError(
                "failure reason is required"
            )

        if self.state not in {
            "PENDING",
            "RUNNING",
        }:
            raise ValueError(
                "remote operation cannot fail from "
                "its current state"
            )

        self.failure = str(reason)
        self.state = "FAILED"
