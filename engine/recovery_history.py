"""Record recovery decisions for review and reliability reporting."""

from dataclasses import dataclass
from datetime import datetime, timezone

from engine.recovery_execution_boundary import RecoveryApprovalDecision


@dataclass(frozen=True)
class RecoveryHistoryEntry:
    plan_id: str
    operation_id: str
    status: str
    reason: str
    recorded_at: datetime

    def projection(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "operation_id": self.operation_id,
            "status": self.status,
            "reason": self.reason,
            "recorded_at": self.recorded_at.isoformat(),
        }


class RecoveryHistory:
    """In-memory append-only history of recovery approval decisions."""

    def __init__(self):
        self._entries: list[RecoveryHistoryEntry] = []
        self._recorded_keys: set[tuple[str, str]] = set()

    @property
    def entries(self) -> tuple[RecoveryHistoryEntry, ...]:
        return tuple(
            sorted(self._entries, key=lambda entry: entry.recorded_at)
        )

    def record(
        self,
        decision: RecoveryApprovalDecision,
    ) -> RecoveryHistoryEntry:
        if not isinstance(decision, RecoveryApprovalDecision):
            raise TypeError(
                "decision must be a RecoveryApprovalDecision"
            )

        key = (decision.plan_id, decision.operation_id)
        if key in self._recorded_keys:
            raise ValueError(
                "A decision for this recovery plan and operation is already recorded"
            )

        entry = RecoveryHistoryEntry(
            plan_id=decision.plan_id,
            operation_id=decision.operation_id,
            status=decision.status.value,
            reason=decision.reason,
            recorded_at=datetime.now(timezone.utc),
        )
        self._entries.append(entry)
        self._recorded_keys.add(key)
        return entry

    def projection(self) -> dict:
        entries = self.entries
        counts: dict[str, int] = {}

        for entry in entries:
            counts[entry.status] = counts.get(entry.status, 0) + 1

        return {
            "total": len(entries),
            "by_status": counts,
            "entries": [entry.projection() for entry in entries],
        }
