import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow
from engine.recovery_plan import (
    RecoveryPlan,
    RecoveryPlanStatus,
    RecoveryRisk,
    RecoveryStep,
)
from engine.recovery_execution_boundary import (
    RecoveryApprovalStatus,
    RecoveryExecutionBoundary,
)


def make_plan(
    *,
    status=RecoveryPlanStatus.READY_FOR_REVIEW,
    authorization=True,
    steps=None,
):
    if steps is None:
        steps = (
            RecoveryStep(
                step_id="step-1",
                description="Inspect affected component",
                risk=RecoveryRisk.LOW,
                requires_authorization=authorization,
            ),
        )
    return RecoveryPlan(
        plan_id="plan-1",
        operation_id="operation-1",
        steps=steps,
        status=status,
    )


def make_boundary():
    return RecoveryExecutionBoundary(
        TechnicianWorkflow(DiagnosticCase())
    )


def test_recovery_requires_explicit_authorization():
    decision = make_boundary().evaluate(make_plan())

    assert decision.status is RecoveryApprovalStatus.DENIED
    assert "authorization" in decision.reason.lower()


def test_explicit_authorization_allows_eligible_plan():
    decision = make_boundary().evaluate(
        make_plan(),
        explicitly_authorized=True,
    )

    assert decision.approved is True


def test_draft_plan_is_denied():
    decision = make_boundary().evaluate(
        make_plan(status=RecoveryPlanStatus.DRAFT),
        explicitly_authorized=True,
    )

    assert decision.approved is False


def test_empty_plan_is_denied():
    decision = make_boundary().evaluate(
        make_plan(steps=()),
        explicitly_authorized=True,
    )

    assert decision.approved is False


def test_plan_not_requiring_authorization_can_be_approved():
    decision = make_boundary().evaluate(
        make_plan(authorization=False),
    )

    assert decision.approved is True


def test_boundary_preserves_canonical_workflow():
    boundary = make_boundary()

    assert isinstance(boundary.workflow, TechnicianWorkflow)


def test_boundary_does_not_expose_execution_methods():
    boundary = make_boundary()

    assert not hasattr(boundary, "execute")
    assert not hasattr(boundary, "execute_recovery")


def test_invalid_plan_is_rejected():
    with pytest.raises(TypeError):
        make_boundary().evaluate(None)


def test_invalid_authorization_flag_is_rejected():
    with pytest.raises(TypeError):
        make_boundary().evaluate(
            make_plan(),
            explicitly_authorized="yes",
        )


def test_decision_projection_is_consistent():
    decision = make_boundary().evaluate(make_plan())

    projection = decision.projection()

    assert projection["status"] == "DENIED"
    assert projection["approved"] is False
