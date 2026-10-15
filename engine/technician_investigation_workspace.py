from copy import deepcopy

from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.investigation_findings import InvestigationFindings


class TechnicianInvestigationWorkspace:
    """
    Canonical V1.0 technician-facing investigation projection.

    This is a presentation/read-only boundary.

    It does not:
    - investigate
    - analyze
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, orchestrator, findings=None):
        if not isinstance(
            orchestrator,
            DiagnosticInvestigationOrchestrator,
        ):
            raise ValueError(
                "TechnicianInvestigationWorkspace requires a "
                "DiagnosticInvestigationOrchestrator."
            )

        if findings is None:
            findings = InvestigationFindings(orchestrator)

        if not isinstance(findings, InvestigationFindings):
            raise ValueError(
                "findings must be an InvestigationFindings."
            )

        self.orchestrator = orchestrator
        self.findings = findings

    @property
    def case(self):
        return self.orchestrator.case

    @property
    def investigation_state(self):
        return self.orchestrator.investigation_state

    def findings_projection(self):
        return deepcopy(self.findings.findings())

    def projection(self):
        return {
            "case_id": self.case.case_id,
            "investigation_state": self.investigation_state,
            "findings": self.findings_projection(),
            "investigation": deepcopy(
                self.orchestrator.result
            ),
        }
