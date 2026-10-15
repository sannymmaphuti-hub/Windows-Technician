import pytest

from engine.bounded_retry_coordinator import BoundedRetryCoordinator
from engine.diagnostic_case import DiagnosticCase
from engine.operation_failure_classifier import (
    OperationFailureCategory,
    OperationFailureClassifier,
)
from engine.operation_lifecycle_tracker import (
    OperationLifecycleTracker,
    OperationStatus,
)
from engine.recovery_execution_boundary import RecoveryApprovalStatus
from engine.recovery_plan import (
    RecoveryPlan,
    RecoveryPlanStatus,
    RecoveryRisk,
    RecoveryStep,
)
from engine.reliability_service import ReliabilityService
from engine.technician_workflow import TechnicianWorkflow


def make_service(maximum_retries=1):
    return ReliabilityService(
        TechnicianWorkflow(DiagnosticCase()),
        maximum_retries=maximum_retries,
    )


def make_failure(
    operation_id="operation-1",
    category=OperationFailureCategory.TIMEOUT,
):
    return OperationFailureClassifier().classify(
        operation_id,
        category,
        "Injected test failure",
    )


def make_plan(
    plan_id="plan-1",
    status=RecoveryPlanStatus.READY_FOR_REVIEW,
    requires_authorization=True,
):
    step = RecoveryStep(
        step_id="step-1",
        description="Inspect affected component",
        risk=RecoveryRisk.MEDIUM,
        requires_authorization=requires_authorization,
    )
    return RecoveryPlan(
        plan_id=plan_id,
        operation_id="operation-1",
        steps=(step,),
        status=status,
    )


def test_operation_cannot_skip_pending_state():
    tracker = OperationLifecycleTracker()
    operation = tracker.create("diagnostic")

    with pytest.raises(ValueError):
        tracker.transition(operation.operation_id, OperationStatus.SUCCEEDED)


def test_terminal_operation_cannot_be_modified():
    tracker = OperationLifecycleTracker()
    operation = tracker.create("diagnostic")
    tracker.transition(operation.operation_id, OperationStatus.CANCELLED)

    with pytest.raises(ValueError):
        tracker.transition(operation.operation_id, OperationStatus.RUNNING)


def test_failure_cannot_be_recorded_without_a_reason():
    tracker = OperationLifecycleTracker()
    operation = tracker.create("diagnostic")
    tracker.transition(operation.operation_id, OperationStatus.RUNNING)

    with pytest.raises(ValueError):
        tracker.transition(
            operation.operation_id,
            OperationStatus.FAILED,
        )


def test_retry_budget_cannot_be_bypassed():
    coordinator = BoundedRetryCoordinator(maximum_retries=1)
    failure = make_failure()

    first = coordinator.evaluate_retry(
        failure,
        explicitly_retry_safe=True,
    )
    second = coordinator.evaluate_retry(
        failure,
        explicitly_retry_safe=True,
    )
    third = coordinator.evaluate_retry(
        failure,
        explicitly_retry_safe=True,
    )

    assert first.approved is True
    assert second.approved is False
    assert third.approved is False


def test_permission_failure_never_receives_retry_approval():
    coordinator = BoundedRetryCoordinator(maximum_retries=3)

    decision = coordinator.evaluate_retry(
        make_failure(category=OperationFailureCategory.PERMISSION_DENIED),
        explicitly_retry_safe=True,
    )

    assert decision.approved is False


def test_unknown_failure_is_not_retryable():
    coordinator = BoundedRetryCoordinator(maximum_retries=3)

    decision = coordinator.evaluate_retry(
        make_failure(category=OperationFailureCategory.UNKNOWN),
        explicitly_retry_safe=True,
    )

    assert decision.approved is False


def test_malformed_failure_evidence_is_rejected():
    classifier = OperationFailureClassifier()

    with pytest.raises(ValueError):
        classifier.classify("operation-1", OperationFailureCategory.TIMEOUT, " ")

    with pytest.raises(ValueError):
        classifier.classify("", OperationFailureCategory.TIMEOUT, "Timeout")


def test_recovery_without_authorization_is_denied_and_recorded():
    service = make_service()

    decision = service.evaluate_recovery(make_plan())

    assert decision.status is RecoveryApprovalStatus.DENIED
    assert service.recovery_history.entries[-1].status == "DENIED"


def test_draft_recovery_plan_cannot_be_approved():
    service = make_service()

    decision = service.evaluate_recovery(
        make_plan(status=RecoveryPlanStatus.DRAFT),
        explicitly_authorized=True,
    )

    assert decision.status is RecoveryApprovalStatus.DENIED


def test_recovery_history_rejects_duplicate_decisions():
    service = make_service()
    plan = make_plan()

    service.evaluate_recovery(plan)

    with pytest.raises(ValueError):
        service.evaluate_recovery(plan)


def test_recovery_authorization_flag_must_be_boolean():
    service = make_service()

    with pytest.raises(TypeError):
        service.evaluate_recovery(
            make_plan(),
            explicitly_authorized="yes",
        )


def test_failure_service_rejects_unstarted_operation():
    service = make_service()
    operation = service.create_operation("diagnostic")

    with pytest.raises(ValueError):
        service.fail_operation(
            operation.operation_id,
            OperationFailureCategory.TIMEOUT,
            "Provider timeout",
            explicitly_retry_safe=True,
        )


def test_reliability_service_does_not_execute_operations():
    service = make_service()

    assert not hasattr(service, "execute_operation")
    assert not hasattr(service, "execute_remediation")
    assert not hasattr(service, "execute_recovery")


def test_recovery_plan_rejects_duplicate_step_identifiers():
    first = RecoveryStep(
        "same-step",
        "Inspect component",
        RecoveryRisk.LOW,
    )
    second = RecoveryStep(
        "same-step",
        "Review component",
        RecoveryRisk.MEDIUM,
    )

    with pytest.raises(ValueError):
        RecoveryPlan(
            "plan-1",
            "operation-1",
            (first, second),
        )
