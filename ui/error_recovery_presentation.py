"""Consistent error, empty, and recovery-state presentation."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ErrorRecoveryPresentation:
    """Project application states into clear, non-destructive UI messages."""

    SCHEMA_VERSION = "1.0"

    _ERROR_MESSAGES = {
        "DIAGNOSTIC_FAILED": (
            "The diagnostic could not be completed. "
            "The underlying system state may still be unknown."
        ),
        "OPERATION_FAILED": (
            "The operation failed. Review the details before trying again."
        ),
        "CONNECTION_LOST": (
            "The connection was lost. The remote system's current state "
            "could not be confirmed."
        ),
        "RECOVERY_REQUIRED": (
            "Recovery requires attention before work can safely continue."
        ),
        "UNKNOWN": (
            "An unexpected problem occurred. The system state could not "
            "be confirmed."
        ),
    }

    _EMPTY_MESSAGES = {
        "NO_FINDINGS": "No findings have been reported.",
        "NO_CASES": "There are no diagnostic cases to display.",
        "NO_HISTORY": "No history is available yet.",
        "NO_RECOMMENDATIONS": "No recommendations are currently available.",
    }

    _RECOVERY_MESSAGES = {
        "AVAILABLE": "A recovery option is available for review.",
        "REQUIRES_AUTHORIZATION": (
            "Recovery requires explicit authorization before execution."
        ),
        "IN_PROGRESS": "Recovery is in progress.",
        "SUCCEEDED": "Recovery completed; verify the resulting system state.",
        "FAILED": "Recovery failed. The system state may require investigation.",
        "UNAVAILABLE": "No recovery option is currently available.",
    }

    def build_error(
        self,
        *,
        error_code: str,
        detail: str = "",
    ) -> dict[str, Any]:
        code = self._validate_code(error_code, "error_code")
        if not isinstance(detail, str):
            raise TypeError("detail must be a string")

        known = code in self._ERROR_MESSAGES
        return {
            "schema_version": self.SCHEMA_VERSION,
            "state_type": "ERROR",
            "code": code if known else "UNKNOWN",
            "message": self._ERROR_MESSAGES.get(
                code, self._ERROR_MESSAGES["UNKNOWN"]
            ),
            "detail": detail.strip(),
            "system_state_confirmed": False
            if code in {"CONNECTION_LOST", "RECOVERY_REQUIRED", "UNKNOWN"}
            or not known
            else None,
            "retry_authorized": False,
            "operation_executed_by_presentation": False,
        }

    def build_empty(
        self,
        *,
        empty_code: str,
    ) -> dict[str, Any]:
        code = self._validate_code(empty_code, "empty_code")
        if code not in self._EMPTY_MESSAGES:
            raise ValueError("unsupported empty_code")

        return {
            "schema_version": self.SCHEMA_VERSION,
            "state_type": "EMPTY",
            "code": code,
            "message": self._EMPTY_MESSAGES[code],
            "items_available": False,
            "operation_executed_by_presentation": False,
        }

    def build_recovery(
        self,
        *,
        recovery_status: str,
        detail: str = "",
    ) -> dict[str, Any]:
        status = self._validate_code(recovery_status, "recovery_status")
        if not isinstance(detail, str):
            raise TypeError("detail must be a string")
        if status not in self._RECOVERY_MESSAGES:
            raise ValueError("unsupported recovery_status")

        return {
            "schema_version": self.SCHEMA_VERSION,
            "state_type": "RECOVERY",
            "status": status,
            "message": self._RECOVERY_MESSAGES[status],
            "detail": detail.strip(),
            "requires_authorization": status == "REQUIRES_AUTHORIZATION",
            "requires_verification": status == "SUCCEEDED",
            "operation_executed_by_presentation": False,
        }

    @staticmethod
    def _validate_code(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")
        if not value.strip():
            raise ValueError(f"{field} must be a non-empty string")
        return value.strip().upper()
