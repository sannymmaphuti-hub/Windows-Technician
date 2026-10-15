from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.system_level_investigation import SystemLevelInvestigation
from engine.technician_workflow import TechnicianWorkflow


class DiagnosticInvestigationOrchestrator:
    """
    Canonical V1.0 investigation orchestration boundary.

    Coordinates the existing TechnicianWorkflow lifecycle with the
    canonical SystemLevelInvestigation engine.

    This class does not:
    - create a new workflow
    - create a new diagnostic case
    - perform root-cause reasoning
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(
        self,
        workflow,
        investigation=None,
    ):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "DiagnosticInvestigationOrchestrator requires "
                "a TechnicianWorkflow."
            )

        if investigation is None:
            investigation = SystemLevelInvestigation()

        if not hasattr(investigation, "investigate"):
            raise ValueError(
                "investigation must provide an investigate() method."
            )

        self.workflow = workflow
        self.investigation = investigation
        self._result = None
        self._investigation_state = "PENDING"

    @property
    def case(self):
        return self.workflow.case

    @property
    def result(self):
        return deepcopy(self._result)

    @property
    def investigation_state(self):
        return self._investigation_state

    def start(self, system_data=None):
        """
        Start the canonical technician investigation lifecycle.

        If explicit system_data is supplied, it is passed through unchanged.
        Otherwise, investigation input is constructed from the canonical
        DiagnosticCase evidence.
        """
        self.workflow.start_investigation()
        self._investigation_state = "RUNNING"

        if system_data is None:
            system_data = self._case_evidence()

        try:
            self._result = self.investigation.investigate(
                deepcopy(system_data)
            )
        except Exception:
            self._investigation_state = "FAILED"
            raise

        self._investigation_state = "COMPLETED"

        return deepcopy(self._result)

    def projection(self):
        return {
            "case": {
                "case_id": self.case.case_id,
            },
            "workflow": {
                "state": self.workflow.state,
                "is_terminal": self.workflow.is_terminal,
            },
            "investigation_state": self.investigation_state,
            "investigation": deepcopy(self._result),
        }

    def _case_evidence(self):
        return {
            "observations": deepcopy(self.case.observations),
            "signals": deepcopy(self.case.signals),
            "correlations": deepcopy(self.case.correlations),
            "findings": deepcopy(self.case.findings),
        }
