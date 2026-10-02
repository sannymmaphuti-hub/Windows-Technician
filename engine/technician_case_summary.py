from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianCaseSummary:

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianCaseSummary requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._decision = None
        self._notes = None
        self._remediation_status = None
        self._verification_status = None
        self._escalation_status = None
        self._closure = None
        self._reasoning_summary = None

    @property
    def workflow(self):
        return self._workflow

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def workflow_id(self):
        return self._workflow.workflow_id

    @property
    def workflow_state(self):
        return self._workflow.state

    @property
    def is_terminal(self):
        return self._workflow.is_terminal

    @property
    def findings(self):
        return list(self._workflow.case.findings)

    @property
    def root_causes(self):
        return list(self._workflow.case.root_causes)

    @property
    def recommendations(self):
        return list(self._workflow.case.recommendations)

    @property
    def decision(self):
        return self._decision

    @property
    def notes(self):
        if self._notes is None:
            return []
        return list(self._notes.notes)

    @property
    def workflow_history(self):
        return self._workflow.history

    @property
    def remediation_status(self):
        return self._remediation_status

    @property
    def verification_status(self):
        return self._verification_status

    @property
    def escalation_status(self):
        return self._escalation_status

    @property
    def closure(self):
        return self._closure

    @property
    def closure_id(self):
        if self._closure is None:
            return None
        return self._closure.closure_id

    @property
    def closure_technician(self):
        if self._closure is None:
            return None
        return self._closure.technician

    @property
    def closure_reason(self):
        if self._closure is None:
            return None
        return self._closure.reason

    @property
    def closure_state(self):
        if self._closure is None:
            return None
        return self._closure.workflow_state

    @property
    def reasoning_summary(self):
        return self._reasoning_summary

    def set_decision(self, decision):
        self._decision = decision

    def set_notes(self, notes):
        self._notes = notes

    def set_remediation_status(self, status):
        self._remediation_status = status

    def set_verification_status(self, status):
        self._verification_status = status

    def set_escalation_status(self, status):
        self._escalation_status = status

    def set_closure(self, closure):
        if not isinstance(
            closure,
            TechnicianCaseClosure,
        ):
            raise ValueError(
                "Case summary requires a TechnicianCaseClosure."
            )

        if closure.workflow is not self._workflow:
            raise ValueError(
                "Closure belongs to a different workflow."
            )

        self._closure = closure

    def set_reasoning_summary(self, reasoning_summary):
        if not isinstance(
            reasoning_summary,
            TechnicianReasoningSummary,
        ):
            raise ValueError(
                "Case summary requires a "
                "TechnicianReasoningSummary."
            )

        if reasoning_summary.workflow is not self._workflow:
            raise ValueError(
                "Reasoning summary belongs to a "
                "different workflow."
            )

        self._reasoning_summary = reasoning_summary