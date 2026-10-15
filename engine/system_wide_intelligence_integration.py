from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.system_level_investigation import SystemLevelInvestigation
from engine.system_problem_relationships import SystemProblemRelationships
from engine.system_root_cause_reasoning import SystemRootCauseReasoning
from engine.system_level_recommendations import SystemLevelRecommendations
from engine.historical_intelligence_integration import (
    HistoricalIntelligenceIntegration,
)


class SystemWideIntelligenceIntegration:
    """
    Canonical V1.0 system-wide intelligence composition boundary.

    Coordinates:
    - system investigation
    - problem relationships
    - root-cause reasoning
    - recommendations
    - historical intelligence

    Historical intelligence is an additional evidence source. It does
    not replace or duplicate the existing intelligence pipeline.

    This class does not:
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(
        self,
        case,
        investigation=None,
        relationships=None,
        root_cause_reasoning=None,
        recommendations=None,
        historical=None,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "SystemWideIntelligenceIntegration requires a DiagnosticCase."
            )

        self.case = case

        self.investigation = (
            investigation
            if investigation is not None
            else SystemLevelInvestigation()
        )

        self.relationships = (
            relationships
            if relationships is not None
            else SystemProblemRelationships()
        )

        self.root_cause_reasoning = (
            root_cause_reasoning
            if root_cause_reasoning is not None
            else SystemRootCauseReasoning()
        )

        self.recommendations = (
            recommendations
            if recommendations is not None
            else SystemLevelRecommendations()
        )

        if historical is not None and not isinstance(
            historical,
            HistoricalIntelligenceIntegration,
        ):
            raise ValueError(
                "historical must be a HistoricalIntelligenceIntegration."
            )

        self.historical = historical

        self._investigation_result = None
        self._relationship_result = None
        self._root_cause_result = None
        self._recommendation_result = None

    def investigate(self, system_data=None):
        self._investigation_result = self.investigation.investigate(
            system_data
        )
        return deepcopy(self._investigation_result)

    def investigation_result(self):
        return deepcopy(self._investigation_result)

    def analyze_relationships(self, evidence):
        self._relationship_result = self.relationships.analyze(
            evidence
        )
        return deepcopy(self._relationship_result)

    def relationship_result(self):
        return deepcopy(self._relationship_result)

    def analyze_root_causes(self, relationships=None):
        if relationships is None:
            relationships = self._relationship_result

        self._root_cause_result = (
            self.root_cause_reasoning.analyze(
                relationships
            )
        )

        return deepcopy(self._root_cause_result)

    def root_cause_result(self):
        return deepcopy(self._root_cause_result)

    def generate_recommendations(self, system_data=None):
        self._recommendation_result = (
            self.recommendations.generate(system_data)
        )

        return deepcopy(self._recommendation_result)

    def recommendation_result(self):
        return deepcopy(self._recommendation_result)

    def historical_projection(self):
        if self.historical is None:
            return {}

        return deepcopy(
            self.historical.projection(
                self.case.machine_id,
                case=self.case,
            )
        )

    def case_projection(self):
        return {
            "case_id": self.case.case_id,
            "observations": deepcopy(self.case.observations),
            "signals": deepcopy(self.case.signals),
            "correlations": deepcopy(self.case.correlations),
            "findings": deepcopy(self.case.findings),
            "root_causes": deepcopy(self.case.root_causes),
            "recommendations": deepcopy(self.case.recommendations),
        }

    def intelligence_projection(self):
        investigation = self._safe_projection(
            self.investigation
        )

        relationships = self._safe_projection(
            self.relationships
        )

        root_causes = self._safe_projection(
            self.root_cause_reasoning
        )

        recommendations = self._safe_projection(
            self.recommendations
        )

        if self._investigation_result is not None:
            investigation = deepcopy(
                self._investigation_result
            )

        if self._relationship_result is not None:
            relationships = deepcopy(
                self._relationship_result
            )

        if self._root_cause_result is not None:
            root_causes = deepcopy(
                self._root_cause_result
            )

        if self._recommendation_result is not None:
            recommendations = deepcopy(
                self._recommendation_result
            )

        projection = {
            "investigation": investigation,
            "relationships": relationships,
            "root_cause_reasoning": root_causes,
            "recommendations": recommendations,
        }

        historical = self.historical_projection()

        if historical:
            projection["historical"] = historical

        return projection

    def projection(self):
        return {
            "case": self.case_projection(),
            "intelligence": self.intelligence_projection(),
        }

    @staticmethod
    def _safe_projection(component):
        if hasattr(component, "projection"):
            return deepcopy(component.projection())

        if hasattr(component, "to_dict"):
            return deepcopy(component.to_dict())

        if isinstance(component, dict):
            return deepcopy(component)

        return {}
