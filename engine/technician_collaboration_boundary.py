from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


class TechnicianCollaborationBoundary:
    """
    Canonical V1.0 technician collaboration boundary.

    This boundary composes the existing DiagnosticCase and
    TechnicianWorkflow without creating a second case lifecycle.

    It is intentionally observational at this stage of Phase 10.
    Collaboration state, ownership, assignment, activity, and
    handoff
    will be layered onto this boundary by the subsequent Phase 10
    services.

    This class does not:
    - create diagnostic cases
    - create workflows
    - diagnose
    - investigate
    - reason
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    - mutate case lifecycle state
    """

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
        self.case = workflow.case

    @property
    def case_id(self):
        """Return the canonical case identifier."""
        return self.case.case_id

    @property
    def machine_id(self):
        """Return the canonical machine identifier."""
        return self.case.machine_id

    @property
    def state(self):
        """Return the canonical workflow state."""
        return self.workflow.state

    @property
    def hostname(self):
        """Return the canonical machine hostname."""
        return self.case.hostname

    @property
    def is_terminal(self):
        """Return whether the canonical workflow is terminal."""
        return self.workflow.is_terminal

    def case_projection(self):
        """
        Return a defensive collaboration-boundary case projection.

        The projection exposes canonical identity and lifecycle state
        only. No mutable canonical object is returned.
        """
        return {
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "hostname": self.hostname,
            "state": self.state.value,
            "is_terminal": self.is_terminal,
        }

    def projection(self):
        """Return the complete read-only collaboration projection."""
        return {
            "case": deepcopy(self.case_projection()),
        }
