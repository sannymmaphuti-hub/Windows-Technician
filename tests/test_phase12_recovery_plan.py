import pytest

from engine.recovery_plan import (
    RecoveryPlan,
    RecoveryPlanStatus,
    RecoveryRisk,
    RecoveryStep,
)


def make_step(step_id="step-1", risk=RecoveryRisk.LOW, authorization=True):
    return RecoveryStep(
        step_id=step_id,
        description="Inspect affected component",
        risk=risk,
        requires_authorization=authorization,
    )


def test_plan_creation_generates_identity():
    plan = RecoveryPlan.create("operation-1", (make_step(),))

    assert plan.plan_id
    assert plan.operation_id == "operation-1"
    assert plan.status is RecoveryPlanStatus.DRAFT


def test_plan_requires_authorization_when_any_step_requires_it():
    plan = RecoveryPlan.create(
        "operation-1",
        (make_step(authorization=False), make_step("step-2", authorization=True)),
    )

    assert plan.requires_authorization is True


def test_plan_without_authorized_steps_does_not_claim_authorization_required():
    plan = RecoveryPlan.create(
        "operation-1",
        (make_step(authorization=False),),
    )

    assert plan.requires_authorization is False


def test_highest_risk_is_reported():
    plan = RecoveryPlan.create(
        "operation-1",
        (
            make_step("step-1", RecoveryRisk.LOW),
            make_step("step-2", RecoveryRisk.CRITICAL),
            make_step("step-3", RecoveryRisk.MEDIUM),
        ),
    )

    assert plan.highest_risk is RecoveryRisk.CRITICAL


def test_empty_plan_has_lowest_risk_and_no_authorization_requirement():
    plan = RecoveryPlan.create("operation-1", ())

    assert plan.highest_risk is RecoveryRisk.LOW
    assert plan.requires_authorization is False


def test_duplicate_step_ids_are_rejected():
    with pytest.raises(ValueError):
        RecoveryPlan.create(
            "operation-1",
            (make_step("duplicate"), make_step("duplicate")),
        )


def test_step_requires_valid_risk():
    with pytest.raises(TypeError):
        RecoveryStep("step-1", "Inspect component", "LOW")


def test_plan_requires_tuple_of_steps():
    with pytest.raises(TypeError):
        RecoveryPlan("plan-1", "operation-1", [make_step()])


def test_projection_is_serializable():
    plan = RecoveryPlan.create("operation-1", (make_step(),))

    projection = plan.projection()

    assert projection["status"] == "DRAFT"
    assert projection["steps"][0]["risk"] == "LOW"
    assert projection["requires_authorization"] is True
