"""Structured recovery plans; definitions only, with no execution."""

from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class RecoveryRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecoveryPlanStatus(str, Enum):
    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class RecoveryStep:
    step_id: str
    description: str
    risk: RecoveryRisk
    requires_authorization: bool = True

    def __post_init__(self):
        if not isinstance(self.step_id, str) or not self.step_id.strip():
            raise ValueError("step_id must be a non-empty string")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.risk, RecoveryRisk):
            raise TypeError("risk must be a RecoveryRisk")
        if not isinstance(self.requires_authorization, bool):
            raise TypeError("requires_authorization must be a bool")

    def projection(self) -> dict:
        return {
            "step_id": self.step_id,
            "description": self.description,
            "risk": self.risk.value,
            "requires_authorization": self.requires_authorization,
        }


@dataclass(frozen=True)
class RecoveryPlan:
    plan_id: str
    operation_id: str
    steps: tuple[RecoveryStep, ...]
    status: RecoveryPlanStatus = RecoveryPlanStatus.DRAFT

    def __post_init__(self):
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("plan_id must be a non-empty string")
        if not isinstance(self.operation_id, str) or not self.operation_id.strip():
            raise ValueError("operation_id must be a non-empty string")
        if not isinstance(self.steps, tuple):
            raise TypeError("steps must be a tuple of RecoveryStep objects")
        if not all(isinstance(step, RecoveryStep) for step in self.steps):
            raise TypeError("every step must be a RecoveryStep")
        if len({step.step_id for step in self.steps}) != len(self.steps):
            raise ValueError("recovery step IDs must be unique")
        if not isinstance(self.status, RecoveryPlanStatus):
            raise TypeError("status must be a RecoveryPlanStatus")

    @classmethod
    def create(
        cls,
        operation_id: str,
        steps: tuple[RecoveryStep, ...],
    ) -> "RecoveryPlan":
        return cls(
            plan_id=str(uuid4()),
            operation_id=operation_id,
            steps=steps,
        )

    @property
    def requires_authorization(self) -> bool:
        return any(step.requires_authorization for step in self.steps)

    @property
    def highest_risk(self) -> RecoveryRisk:
        order = {
            RecoveryRisk.LOW: 0,
            RecoveryRisk.MEDIUM: 1,
            RecoveryRisk.HIGH: 2,
            RecoveryRisk.CRITICAL: 3,
        }
        return max(
            (step.risk for step in self.steps),
            key=order.__getitem__,
            default=RecoveryRisk.LOW,
        )

    def projection(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "operation_id": self.operation_id,
            "status": self.status.value,
            "requires_authorization": self.requires_authorization,
            "highest_risk": self.highest_risk.value,
            "steps": [step.projection() for step in self.steps],
        }
