"""Explicit, conservative retry eligibility policy."""

from dataclasses import dataclass

from engine.operation_failure_classifier import (
    OperationFailure,
    OperationFailureCategory,
)


@dataclass(frozen=True)
class RetryEligibilityDecision:
    eligible: bool
    reason: str
    operation_id: str
    category: str

    def projection(self) -> dict:
        return {
            "eligible": self.eligible,
            "reason": self.reason,
            "operation_id": self.operation_id,
            "category": self.category,
        }


class RetryEligibilityPolicy:
    """Determine retry eligibility without scheduling or executing retries."""

    _RETRYABLE_CATEGORIES = frozenset({
        OperationFailureCategory.TRANSIENT,
        OperationFailureCategory.TIMEOUT,
        OperationFailureCategory.RESOURCE_UNAVAILABLE,
    })

    def evaluate(
        self,
        failure: OperationFailure,
        *,
        explicitly_retry_safe: bool = False,
        retry_budget_remaining: bool = False,
    ) -> RetryEligibilityDecision:
        if not isinstance(failure, OperationFailure):
            raise TypeError("failure must be an OperationFailure")

        if not isinstance(explicitly_retry_safe, bool):
            raise TypeError("explicitly_retry_safe must be a bool")

        if not isinstance(retry_budget_remaining, bool):
            raise TypeError("retry_budget_remaining must be a bool")

        if failure.category not in self._RETRYABLE_CATEGORIES:
            eligible = False
            reason = "Failure category is not eligible for automatic retry."
        elif not failure.retryable_candidate:
            eligible = False
            reason = "Failure classification does not permit retry consideration."
        elif not explicitly_retry_safe:
            eligible = False
            reason = "Operation has not been explicitly declared retry-safe."
        elif not retry_budget_remaining:
            eligible = False
            reason = "No retry budget remains."
        else:
            eligible = True
            reason = "Retry eligibility conditions are satisfied."

        return RetryEligibilityDecision(
            eligible=eligible,
            reason=reason,
            operation_id=failure.operation_id,
            category=failure.category.value,
        )
