from copy import deepcopy

from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.system_problem_relationships import SystemProblemRelationships


class CrossDomainDiagnosticReasoning:
    """
    Canonical V1.0 cross-domain diagnostic reasoning boundary.

    Reuses the existing SystemProblemRelationships engine to identify
    relationships between evidence originating from different diagnostic
    domains.

    This class does not:
    - create DiagnosticCase objects
    - create workflows
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, orchestrator, relationships=None):
        if not isinstance(
            orchestrator,
            DiagnosticInvestigationOrchestrator,
        ):
            raise ValueError(
                "CrossDomainDiagnosticReasoning requires a "
                "DiagnosticInvestigationOrchestrator."
            )

        if relationships is None:
            relationships = SystemProblemRelationships()

        if not hasattr(relationships, "analyze"):
            raise ValueError(
                "relationships must provide an analyze() method."
            )

        self.orchestrator = orchestrator
        self.relationships = relationships
        self._result = None

    @property
    def result(self):
        return deepcopy(self._result)

    def analyze(self):
        evidence = self._investigation_evidence()

        self._result = self.relationships.analyze(
            deepcopy(evidence)
        )

        return deepcopy(self._result)

    def projection(self):
        return {
            "case_id": self.orchestrator.case.case_id,
            "relationships": deepcopy(self._result),
        }

    def _investigation_evidence(self):
        result = self.orchestrator.result

        if isinstance(result, dict):
            return deepcopy(result)

        return {
            "investigation": deepcopy(result),
        }
