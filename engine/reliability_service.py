"""Coordinate reliability services without executing system operations."""

from engine.bounded_retry_coordinator import (
    BoundedRetryCoordinator,
    RetryAttemptDecision,
)
from engine.operation_failure_classifier import (
    OperationFailure,
    OperationFailureCategory,
    OperationFailureClassifier,
)
from engine.operation_lifecycle_tracker import (
    OperationLifecycleTracker,
    OperationRecord,
    OperationStatus,
)
from engine.recovery_execution_boundary import (
    RecoveryApprovalDecision,
    RecoveryExecutionBoundary,
)
from engine.recovery_history import RecoveryHistory
from engine.recovery_plan import RecoveryPlan
from engine.reliability_boundary import ReliabilityBoundary
from engine.retry_eligibility_policy import RetryEligibilityPolicy
from engine.technician_workflow import TechnicianWorkflow


class ReliabilityService:
    """Coordinate operation tracking, retry decisions, and recovery review.

    This service records state and decisions only. It does not execute
    diagnostics, remediation, retries, or recovery steps.
    """

    def __init__(
        self,
        workflow: TechnicianWorkflow,
        *,
        maximum_retries: int = 2,
    ):
        self._boundary = ReliabilityBoundary(workflow)
        self._operations = OperationLifecycleTracker()
        self._failure_classifier = OperationFailureClassifier()
        self._retry_policy = RetryEligibilityPolicy()
        self._retry_coordinator = BoundedRetryCoordinator(
            maximum_retries=maximum_retries,
            eligibility_policy=self._retry_policy,
        )
        self._recovery_boundary = RecoveryExecutionBoundary(workflow)
        self._recovery_history = RecoveryHistory()

    @property
    def workflow(self) -> TechnicianWorkflow:
        return self._boundary.workflow

    @property
    def operations(self) -> OperationLifecycleTracker:
        return self._operations

    @property
    def recovery_history(self) -> RecoveryHistory:
        return self._recovery_history

    def create_operation(self, operation_type: str) -> OperationRecord:
        return self._operations.create(operation_type)

    def start_operation(self, operation_id: str) -> OperationRecord:
        return self._operations.transition(
            operation_id,
            OperationStatus.RUNNING,
        )

    def complete_operation(self, operation_id: str) -> OperationRecord:
        return self._operations.transition(
            operation_id,
            OperationStatus.SUCCEEDED,
        )

    def fail_operation(
        self,
        operation_id: str,
        category: OperationFailureCategory,
        reason: str,
        *,
        explicitly_retry_safe: bool = False,
    ) -> tuple[OperationRecord, OperationFailure, RetryAttemptDecision]:
        """Record a failure and assess retry eligibility without retrying."""
        current = self._operations.get(operation_id)

        if current.status is not OperationStatus.RUNNING:
            raise ValueError("Only a running operation can be marked failed")

        failure = self._failure_classifier.classify(
            operation_id,
            category,
            reason,
        )

        failed_record = self._operations.transition(
            operation_id,
            OperationStatus.FAILED,
            failure_reason=failure.reason,
        )

        retry_decision = self._retry_coordinator.evaluate_retry(
            failure,
            explicitly_retry_safe=explicitly_retry_safe,
        )

        return failed_record, failure, retry_decision

    def evaluate_recovery(
        self,
        plan: RecoveryPlan,
        *,
        explicitly_authorized: bool = False,
    ) -> RecoveryApprovalDecision:
        """Evaluate and record a recovery decision; execute no recovery."""
        decision = self._recovery_boundary.evaluate(
            plan,
            explicitly_authorized=explicitly_authorized,
        )
        self._recovery_history.record(decision)
        return decision

    def projection(self) -> dict:
        operations = self._operations.projection()
        retries = self._retry_coordinator.projection()
        recovery = self._recovery_history.projection()

        return {
            "operation_summary": {
                "total": operations["total"],
                "by_status": operations["by_status"],
            },
            "retry_summary": {
                "maximum_retries": retries["maximum_retries"],
                "approved_retries": retries["approved_retries"],
                "decision_count": len(retries["decisions"]),
            },
            "recovery_summary": {
                "total": recovery["total"],
                "by_status": recovery["by_status"],
            },
        }
