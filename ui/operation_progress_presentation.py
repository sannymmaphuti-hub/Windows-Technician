"""Progress presentation for long-running technician operations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OperationProgress:
    operation_id: str
    status: str
    message: str
    percentage: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError("operation_id must be a non-empty string")

        if not isinstance(self.status, str) or not self.status.strip():
            raise ValueError("status must be a non-empty string")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string")

        if self.percentage is not None:
            if isinstance(self.percentage, bool) or not isinstance(
                self.percentage, int
            ):
                raise TypeError("percentage must be an integer or None")

            if not 0 <= self.percentage <= 100:
                raise ValueError("percentage must be between 0 and 100")


class OperationProgressPresentation:
    """Convert operation progress into a stable, UI-friendly projection."""

    SCHEMA_VERSION = "1.0"

    _STATES = {
        "PENDING": "Waiting to start.",
        "RUNNING": "Operation in progress.",
        "SUCCEEDED": "Operation completed successfully.",
        "FAILED": "Operation failed.",
        "CANCELLED": "Operation was cancelled.",
    }

    _TERMINAL_STATES = {"SUCCEEDED", "FAILED", "CANCELLED"}

    def build(self, progress: OperationProgress) -> dict[str, Any]:
        if not isinstance(progress, OperationProgress):
            raise TypeError("progress must be an OperationProgress")

        status = progress.status.strip().upper()
        if status not in self._STATES:
            raise ValueError(f"unsupported operation status: {progress.status}")

        percentage = progress.percentage

        if status == "SUCCEEDED":
            percentage = 100
        elif status in {"FAILED", "CANCELLED"} and percentage is None:
            percentage = None

        return {
            "schema_version": self.SCHEMA_VERSION,
            "operation_id": progress.operation_id,
            "status": status,
            "message": progress.message,
            "status_summary": self._STATES[status],
            "percentage": percentage,
            "indeterminate": percentage is None,
            "terminal": status in self._TERMINAL_STATES,
            "diagnostics_executed": False,
            "remediation_executed": False,
        }
