from copy import deepcopy

from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)


class InvestigationFindings:
    """
    Canonical V1.0 investigation findings projection.

    Extracts structured findings from the investigation result without
    mutating DiagnosticCase.

    DiagnosticCase integration is intentionally owned by Phase 5.6.
    """

    def __init__(self, orchestrator):
        if not isinstance(
            orchestrator,
            DiagnosticInvestigationOrchestrator,
        ):
            raise ValueError(
                "InvestigationFindings requires a "
                "DiagnosticInvestigationOrchestrator."
            )

        self.orchestrator = orchestrator

    def collect(self):
        findings = self._extract_findings()
        return deepcopy(findings)

    def findings(self):
        return deepcopy(self._extract_findings())

    def projection(self):
        return {
            "case_id": self.orchestrator.case.case_id,
            "findings": self.findings(),
        }

    def _extract_findings(self):
        result = self.orchestrator.result

        if not isinstance(result, dict):
            return []

        findings = result.get("findings", [])

        if not isinstance(findings, list):
            return []

        return deepcopy(findings)
