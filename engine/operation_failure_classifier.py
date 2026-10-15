"""Classify operation failures for safe reliability decisions."""

from dataclasses import dataclass
from enum import Enum


class OperationFailureCategory(str, Enum):
    TRANSIENT = "TRANSIENT"
    TIMEOUT = "TIMEOUT"
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED = "UNSUPPORTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class OperationFailure:
    operation_id: str
    category: OperationFailureCategory
    reason: str
    retryable_candidate: bool

    def projection(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "category": self.category.value,
            "reason": self.reason,
            "retryable_candidate": self.retryable_candidate,
        }


class OperationFailureClassifier:
    """Map explicit failure evidence to conservative categories."""

    _RETRYABLE_CANDIDATES = {
        OperationFailureCategory.TRANSIENT,
        OperationFailureCategory.TIMEOUT,
        OperationFailureCategory.RESOURCE_UNAVAILABLE,
    }

    def classify(
        self,
        operation_id: str,
        category: OperationFailureCategory,
        reason: str,
    ) -> OperationFailure:
        if not isinstance(operation_id, str) or not operation_id.strip():
            raise ValueError("operation_id must be a non-empty string")

        if not isinstance(category, OperationFailureCategory):
            raise ValueError("category must be an OperationFailureCategory")

        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("reason must be a non-empty string")

        return OperationFailure(
            operation_id=operation_id.strip(),
            category=category,
            reason=reason.strip(),
            retryable_candidate=category in self._RETRYABLE_CANDIDATES,
        )
