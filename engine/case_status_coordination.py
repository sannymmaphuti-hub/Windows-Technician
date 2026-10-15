from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


class CaseStatusCoordinator:
    """
    Canonical V1.0 case status coordination boundary.

    The existing TechnicianWorkflow remains the sole authority for
    diagnostic case lifecycle state.

    This class translates that canonical lifecycle into a
    technician-collaboration status projection.

    It does not create or maintain a competing lifecycle.
    """

    STATUS_LABELS = {
        "OPEN": "OPEN",
        "INVESTIGATING": "INVESTIGATING",
        "DIAGNOSED": "DIAGNOSED",
        "ACTION_REQUIRED": "ACTION_REQUIRED",
        "REMEDIATING": "REMEDIATING",
        "VERIFYING": "VERIFYING",
        "RESOLVED": "RESOLVED",
        "CLOSED": "CLOSED",
    }

    TERMINAL_STATES = {
        "RESOLVED",
        "CLOSED",
    }

    def __init__(self, workflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "workflow must be a TechnicianWorkflow."
            )

        if not isinstance(workflow.case, DiagnosticCase):
            raise ValueError(
                "workflow.case must be a DiagnosticCase."
            )

        self.workflow = workflow

    @property
    def case(self):
        """Return the canonical DiagnosticCase."""
        return self.workflow.case

    @property
    def case_id(self):
        """Return the canonical case identifier."""
        return self.case.case_id

    @property
    def state(self):
        """Return the canonical workflow state."""
        return self.workflow.state

    @property
    def status(self):
        """Return the collaboration-readable lifecycle status."""
        return self.STATUS_LABELS.get(
            self.state.value,
            self.state.value,
        )

    @property
    def is_terminal(self):
        """Return whether the canonical workflow is terminal."""
        return self.state.value in self.TERMINAL_STATES

    @property
    def is_active(self):
        """Return whether the canonical workflow is non-terminal."""
        return not self.is_terminal

    def projection(self):
        """Return a defensive status projection."""
        return deepcopy(
            {
                "case_id": self.case_id,
                "state": self.state.value,
                "status": self.status,
                "is_active": self.is_active,
                "is_terminal": self.is_terminal,
            }
        )

    def __repr__(self):
        return (
            "CaseStatusCoordinator("
            f"case_id={self.case_id!r}, "
            f"state={self.state.value!r}, "
            f"is_terminal={self.is_terminal!r}"
            ")"
        )
