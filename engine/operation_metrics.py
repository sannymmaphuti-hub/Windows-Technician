"""Read-only operation metrics for Windows Technician V1.0."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any


class OperationMetricsCollector:
    """Calculate operation metrics from an existing lifecycle tracker.

    This component observes records only. It never creates, starts, completes,
    retries, or modifies operations.
    """

    TERMINAL_STATUSES = frozenset({"SUCCEEDED", "FAILED", "CANCELLED"})
    KNOWN_STATUSES = (
        "PENDING",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "CANCELLED",
    )

    def __init__(self, lifecycle_tracker: Any) -> None:
        if lifecycle_tracker is None:
            raise TypeError("lifecycle_tracker is required.")

        if not hasattr(lifecycle_tracker, "records"):
            raise TypeError("lifecycle_tracker must expose records.")

        self._lifecycle_tracker = lifecycle_tracker

    @staticmethod
    def _status_name(record: Any) -> str:
        if isinstance(record, Mapping):
            status = record.get("status")
        else:
            status = getattr(record, "status", None)

        if status is None:
            return "UNKNOWN"

        value = getattr(status, "value", status)
        if not isinstance(value, str):
            return "UNKNOWN"

        normalized = value.strip().upper()
        return normalized or "UNKNOWN"

    def _snapshot_records(self) -> tuple[Any, ...]:
        """Read the current records without retaining a mutable snapshot."""
        records = self._lifecycle_tracker.records

        if isinstance(records, Mapping):
            return tuple(records.values())

        try:
            return tuple(records)
        except TypeError as exc:
            raise TypeError(
                "lifecycle_tracker.records must be a mapping or iterable."
            ) from exc

    def projection(self) -> dict[str, Any]:
        """Return a fresh, read-only-in-effect metrics snapshot."""
        records = self._snapshot_records()
        counts = Counter(self._status_name(record) for record in records)

        by_status = {
            status: counts.get(status, 0)
            for status in self.KNOWN_STATUSES
        }

        unknown_count = counts.get("UNKNOWN", 0) + sum(
            count
            for status, count in counts.items()
            if status not in self.KNOWN_STATUSES and status != "UNKNOWN"
        )

        total = len(records)
        succeeded = by_status["SUCCEEDED"]
        failed = by_status["FAILED"]
        cancelled = by_status["CANCELLED"]
        terminal = succeeded + failed + cancelled

        return {
            "total_operations": total,
            "by_status": by_status,
            "unknown_status_count": unknown_count,
            "succeeded_count": succeeded,
            "failed_count": failed,
            "cancelled_count": cancelled,
            "running_count": by_status["RUNNING"],
            "pending_count": by_status["PENDING"],
            "terminal_count": terminal,
            "success_rate": succeeded / terminal if terminal else 0.0,
            "failure_rate": failed / terminal if terminal else 0.0,
            "completion_rate": terminal / total if total else 0.0,
        }
