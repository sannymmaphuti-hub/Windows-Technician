"""Track operation lifecycle without executing operations."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class OperationStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OperationRecord:
    operation_id: str
    operation_type: str
    status: OperationStatus
    created_at: datetime
    updated_at: datetime
    failure_reason: str = ""

    def projection(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "operation_type": self.operation_type,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "failure_reason": self.failure_reason,
        }


class OperationLifecycleTracker:
    """Maintain an in-memory record of operation state transitions."""

    _TRANSITIONS = {
        OperationStatus.PENDING: {
            OperationStatus.RUNNING,
            OperationStatus.CANCELLED,
        },
        OperationStatus.RUNNING: {
            OperationStatus.SUCCEEDED,
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
        },
        OperationStatus.SUCCEEDED: set(),
        OperationStatus.FAILED: set(),
        OperationStatus.CANCELLED: set(),
    }

    def __init__(self):
        self._records = {}

    @property
    def records(self) -> tuple[OperationRecord, ...]:
        return tuple(self._records.values())

    def create(self, operation_type: str) -> OperationRecord:
        if not isinstance(operation_type, str) or not operation_type.strip():
            raise ValueError("operation_type must be a non-empty string")

        now = datetime.now(timezone.utc)
        record = OperationRecord(
            operation_id=str(uuid4()),
            operation_type=operation_type.strip(),
            status=OperationStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._records[record.operation_id] = record
        return record

    def get(self, operation_id: str) -> OperationRecord:
        try:
            return self._records[operation_id]
        except (KeyError, TypeError):
            raise KeyError("Unknown operation_id") from None

    def transition(
        self,
        operation_id: str,
        new_status: OperationStatus,
        failure_reason: str = "",
    ) -> OperationRecord:
        record = self.get(operation_id)

        if not isinstance(new_status, OperationStatus):
            raise ValueError("new_status must be an OperationStatus")

        if new_status not in self._TRANSITIONS[record.status]:
            raise ValueError(
                f"Invalid operation transition: "
                f"{record.status.value} -> {new_status.value}"
            )

        if new_status == OperationStatus.FAILED:
            if not isinstance(failure_reason, str) or not failure_reason.strip():
                raise ValueError("A failed operation requires a failure_reason")
        elif failure_reason:
            raise ValueError(
                "failure_reason is only accepted when marking an operation FAILED"
            )

        updated = OperationRecord(
            operation_id=record.operation_id,
            operation_type=record.operation_type,
            status=new_status,
            created_at=record.created_at,
            updated_at=datetime.now(timezone.utc),
            failure_reason=failure_reason.strip() if failure_reason else "",
        )
        self._records[operation_id] = updated
        return updated

    def projection(self) -> dict:
        records = self.records
        return {
            "total": len(records),
            "by_status": {
                status.value: sum(
                    record.status == status for record in records
                )
                for status in OperationStatus
            },
            "operations": [record.projection() for record in records],
        }
