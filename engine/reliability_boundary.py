"""Reliability boundary for canonical technician workflows."""

from engine.technician_workflow import TechnicianWorkflow


class ReliabilityBoundary:
    """Connect reliability coordination to the existing workflow.

    This boundary deliberately does not authorize or execute remediation.
    Recovery and retry policies must preserve the canonical workflow.
    """

    __slots__ = ("_workflow",)

    def __init__(self, workflow: TechnicianWorkflow):
        if not isinstance(workflow, TechnicianWorkflow):
            raise TypeError(
                "workflow must be an instance of TechnicianWorkflow"
            )

        self._workflow = workflow

    @property
    def workflow(self) -> TechnicianWorkflow:
        """Return the canonical workflow managed by this boundary."""
        return self._workflow
