"""Controlled recovery approval boundary; no system changes are executed."""

from dataclasses import dataclass
from enum import Enum

from engine.recovery_plan import RecoveryPlan, RecoveryPlanStatus
from engine.technician_workflow import TechnicianWorkflow


class RecoveryApprovalStatus(str, Enum):
    DENIED = "DENIED"
    APPROVED = "APPROVED"


@dataclass(frozen=True)
class RecoveryApprovalDecision:
    plan_id: str
    operation_id: str
    status: RecoveryApprovalStatus
    reason: str

    @property
    def approved(self) -> bool:
        return self.status is RecoveryApprovalStatus.APPROVED

    def projection(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "operation_id": self.operation_id,
            "status": self.status.value,
            "approved": self.approved,
            "reason": self.reason,
        }


class RecoveryExecutionBoundary:
    """Validate recovery approval conditions without executing recovery."""

    def __init__(self, workflow: TechnicianWorkflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise TypeError("workflow must be a TechnicianWorkflow")
        self._workflow = workflow

    @property
    def workflow(self) -> TechnicianWorkflow:
        return self._workflow

    def evaluate(
        self,
        plan: RecoveryPlan,
        *,
        explicitly_authorized: bool = False,
    ) -> RecoveryApprovalDecision:
        if not isinstance(plan, RecoveryPlan):
            raise TypeError("plan must be a RecoveryPlan")
        if not isinstance(explicitly_authorized, bool):
            raise TypeError("explicitly_authorized must be a bool")

        if plan.status is not RecoveryPlanStatus.READY_FOR_REVIEW:
            return self._deny(
                plan,
                "Recovery plan is not ready for review.",
            )

        if not plan.steps:
            return self._deny(plan, "Recovery plan contains no steps.")

        if plan.requires_authorization and not explicitly_authorized:
            return self._deny(
                plan,
                "Explicit authorization is required for this recovery plan.",
            )

        return RecoveryApprovalDecision(
            plan_id=plan.plan_id,
            operation_id=plan.operation_id,
            status=RecoveryApprovalStatus.APPROVED,
            reason="Recovery approval conditions are satisfied.",
        )

    @staticmethod
    def _deny(plan: RecoveryPlan, reason: str) -> RecoveryApprovalDecision:
        return RecoveryApprovalDecision(
            plan_id=plan.plan_id,
            operation_id=plan.operation_id,
            status=RecoveryApprovalStatus.DENIED,
            reason=reason,
        )
