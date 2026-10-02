import uuid
from datetime import datetime, timezone
from enum import Enum

from engine.recommendation import Recommendation
from engine.technician_workflow import TechnicianWorkflow


class TechnicianDecisionType(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    DEFER = "DEFER"
    INVESTIGATE_FURTHER = "INVESTIGATE_FURTHER"
    ESCALATE = "ESCALATE"


class TechnicianDecision:
    def __init__(
        self,
        workflow,
        recommendation,
        decision_type,
        notes="",
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianDecision requires a TechnicianWorkflow."
            )

        if not isinstance(recommendation, Recommendation):
            raise ValueError(
                "TechnicianDecision requires a Recommendation."
            )

        if not isinstance(decision_type, TechnicianDecisionType):
            raise ValueError(
                "TechnicianDecision requires a valid decision type."
            )

        if not isinstance(notes, str):
            raise ValueError(
                "TechnicianDecision notes must be a string."
            )

        self._decision_id = str(uuid.uuid4())
        self._created_at = datetime.now(timezone.utc)
        self._workflow = workflow
        self._recommendation = recommendation
        self._decision_type = decision_type
        self._notes = notes

    @property
    def decision_id(self):
        return self._decision_id

    @property
    def created_at(self):
        return self._created_at

    @property
    def workflow(self):
        return self._workflow

    @property
    def recommendation(self):
        return self._recommendation

    @property
    def decision_type(self):
        return self._decision_type

    @property
    def notes(self):
        return self._notes