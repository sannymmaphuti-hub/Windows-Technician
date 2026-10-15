import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.operation_failure_classifier import OperationFailureCategory
from engine.operation_lifecycle_tracker import OperationStatus
from engine.recovery_execution_boundary import RecoveryApprovalStatus
from engine.recovery_plan import (
    RecoveryPlan,
    RecoveryPlanStatus,
    RecoveryRisk,
    RecoveryStep,
)
from engine.reliability_service import ReliabilityService
from engine.technician_workflow import TechnicianWorkflow


def make_service(maximum_retries=2):
    workflow = TechnicianWorkflow(DiagnosticCase())
    return ReliabilityService(
        workflow,
        maximum_retries=maximum_retries,
    )


def make_recovery_plan(
    plan_id="plan-1",
    operation_id="operation-1",
    status=RecoveryPlanStatus.READY_FOR_REVIEW,
):
    step = RecoveryStep(
        step_id="step-1",
        description="Inspect affected component",
        risk=RecoveryRisk.LOW,
        requires_authorization=True,
    )
    return RecoveryPlan(
        plan_id=plan_id,
        operation_id=operation_id,
        steps=(step,),
        status=status,
    )


def test_service_preserves_canonical_workflow():
    service = make_service()

    assert service.workflow is not None
    assert hasattr(service.workflow, "reopen")


def test_operation_lifecycle_completes_successfully():
    service = make_service()
    operation = service.create_operation("diagnostic")

    running = service.start_operation(operation.operation_id)
    completed = service.complete_operation(operation.operation_id)

    assert running.status is OperationStatus.RUNNING
    assert completed.status is OperationStatus.SUCCEEDED


def test_failure_is_classified_and_retry_is_denied_by_default():
    service = make_service()
    operation = service.create_operation("diagnostic")
    service.start_operation(operation.operation_id)

    failed, failure, retry = service.fail_operation(
        operation.operation_id,
        OperationFailureCategory.TIMEOUT,
        "Provider timed out",
    )

    assert failed.status is OperationStatus.FAILED
    assert failure.category is OperationFailureCategory.TIMEOUT
    assert retry.approved is False


def test_explicitly_safe_failure_can_receive_bounded_retry_approval():
    service = make_service(maximum_retries=1)
    operation = service.create_operation("read_only_health_check")
    service.start_operation(operation.operation_id)

    _, _, retry = service.fail_operation(
        operation.operation_id,
        OperationFailureCategory.TRANSIENT,
        "Temporary provider interruption",
        explicitly_retry_safe=True,
    )

    assert retry.approved is True
    assert retry.attempt_number == 1


def test_failure_cannot_be_recorded_for_non_running_operation():
    service = make_service()
    operation = service.create_operation("diagnostic")

    with pytest.raises(ValueError):
        service.fail_operation(
            operation.operation_id,
            OperationFailureCategory.UNKNOWN,
            "Unclassified failure",
        )


def test_recovery_requires_explicit_authorization():
    service = make_service()

    decision = service.evaluate_recovery(make_recovery_plan())

    assert decision.status is RecoveryApprovalStatus.DENIED
    assert len(service.recovery_history.entries) == 1


def test_authorized_recovery_decision_is_recorded():
    service = make_service()

    decision = service.evaluate_recovery(
        make_recovery_plan(),
        explicitly_authorized=True,
    )

    assert decision.status is RecoveryApprovalStatus.APPROVED
    assert service.recovery_history.entries[0].status == "APPROVED"


def test_recovery_history_rejects_duplicate_plan_decision():
    service = make_service()
    plan = make_recovery_plan()

    service.evaluate_recovery(plan)

    with pytest.raises(ValueError):
        service.evaluate_recovery(plan)


def test_service_projection_summarizes_all_components():
    service = make_service()
    operation = service.create_operation("diagnostic")
    service.start_operation(operation.operation_id)

    service.fail_operation(
        operation.operation_id,
        OperationFailureCategory.UNKNOWN,
        "Provider returned an unexpected result",
    )
    service.evaluate_recovery(make_recovery_plan())

    projection = service.projection()

    assert projection["operation_summary"]["total"] == 1
    assert projection["operation_summary"]["by_status"]["FAILED"] == 1
    assert projection["retry_summary"]["decision_count"] == 1
    assert projection["recovery_summary"]["total"] == 1


def test_service_does_not_expose_operation_execution_method():
    service = make_service()

    assert not hasattr(service, "execute_operation")
    assert not hasattr(service, "execute_remediation")
    assert not hasattr(service, "execute_recovery")
