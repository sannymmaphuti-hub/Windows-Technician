from copy import deepcopy

from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.investigation_findings import InvestigationFindings


class DiagnosticInvestigationCaseIntegration:
    """
    Canonical V1.0 boundary between investigation findings and
    DiagnosticCase.

    Investigation owns investigation processing.
    DiagnosticCase owns canonical case findings.
    """

    def __init__(self, orchestrator, findings=None):
        if not isinstance(
            orchestrator,
            DiagnosticInvestigationOrchestrator,
        ):
            raise ValueError(
                "DiagnosticInvestigationCaseIntegration requires a "
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

    def integrate_findings(self):
        findings = self.findings.collect()

        self.case.set_findings(
            deepcopy(findings)
        )

        return deepcopy(self.case.findings)

    def projection(self):
        return {
            "case_id": self.case.case_id,
            "findings": deepcopy(self.case.findings),
        }
