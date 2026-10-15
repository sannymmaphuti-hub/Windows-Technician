"""Bounded retry coordination with explicit eligibility checks."""

from dataclasses import dataclass

from engine.operation_failure_classifier import OperationFailure
from engine.retry_eligibility_policy import (
    RetryEligibilityDecision,
    RetryEligibilityPolicy,
)


@dataclass(frozen=True)
class RetryAttemptDecision:
    operation_id: str
    attempt_number: int
    approved: bool
    reason: str
    maximum_retries: int

    def projection(self) -> dict:
        return {
            "operation_id": self.operation_id,
            "attempt_number": self.attempt_number,
            "approved": self.approved,
            "reason": self.reason,
            "maximum_retries": self.maximum_retries,
        }


class BoundedRetryCoordinator:
    """Approve bounded retry attempts; never execute operations."""

    def __init__(
        self,
        maximum_retries: int = 2,
        eligibility_policy: RetryEligibilityPolicy | None = None,
    ):
        if (
            isinstance(maximum_retries, bool)
            or not isinstance(maximum_retries, int)
            or maximum_retries < 0
        ):
            raise ValueError("maximum_retries must be a non-negative integer")

        if eligibility_policy is not None and not isinstance(
            eligibility_policy, RetryEligibilityPolicy
        ):
            raise TypeError(
                "eligibility_policy must be a RetryEligibilityPolicy"
            )

        self._maximum_retries = maximum_retries
        self._eligibility_policy = (
            eligibility_policy or RetryEligibilityPolicy()
        )
        self._attempts: dict[str, int] = {}
        self._history: list[RetryAttemptDecision] = []

    @property
    def maximum_retries(self) -> int:
        return self._maximum_retries

    @property
    def history(self) -> tuple[RetryAttemptDecision, ...]:
        return tuple(self._history)

    def evaluate_retry(
        self,
        failure: OperationFailure,
        *,
        explicitly_retry_safe: bool = False,
    ) -> RetryAttemptDecision:
        if not isinstance(failure, OperationFailure):
            raise TypeError("failure must be an OperationFailure")

        operation_id = failure.operation_id
        retries_used = self._attempts.get(operation_id, 0)

        if retries_used >= self._maximum_retries:
            decision = RetryAttemptDecision(
                operation_id=operation_id,
                attempt_number=retries_used + 1,
                approved=False,
                reason="Maximum retry budget exhausted.",
                maximum_retries=self._maximum_retries,
            )
            self._history.append(decision)
            return decision

        eligibility: RetryEligibilityDecision = (
            self._eligibility_policy.evaluate(
                failure,
                explicitly_retry_safe=explicitly_retry_safe,
                retry_budget_remaining=True,
            )
        )

        approved = eligibility.eligible
        decision = RetryAttemptDecision(
            operation_id=operation_id,
            attempt_number=retries_used + 1,
            approved=approved,
            reason=eligibility.reason,
            maximum_retries=self._maximum_retries,
        )

        if approved:
            self._attempts[operation_id] = retries_used + 1

        self._history.append(decision)
        return decision

    def projection(self) -> dict:
        return {
            "maximum_retries": self._maximum_retries,
            "operations_with_approved_retries": len(self._attempts),
            "approved_retries": sum(self._attempts.values()),
            "decisions": [item.projection() for item in self._history],
        }
