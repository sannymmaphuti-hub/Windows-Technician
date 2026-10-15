from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Type

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.system_level_investigation import SystemLevelInvestigation
from engine.system_level_recommendations import SystemLevelRecommendations
from engine.system_problem_relationships import SystemProblemRelationships
from engine.system_root_cause_reasoning import SystemRootCauseReasoning
from engine.system_wide_intelligence import SystemWideIntelligence
from engine.windows_diagnostic_engine_registry import WindowsDiagnosticEngineRegistry
from packaging.remediation_authorization import RemediationAuthorization


@dataclass(frozen=True)
class V1CanonicalComponents:
    """
    Canonical V1.0 composition of the existing V0.9 platform.

    This class is deliberately a composition boundary.

    It does not implement diagnostic reasoning itself. Instead it
    exposes the existing canonical components as one production
    platform surface.
    """

    diagnostic_case_type: Final[Type[DiagnosticCase]] = DiagnosticCase
    diagnostic_registry_type: Final[
        Type[WindowsDiagnosticEngineRegistry]
    ] = WindowsDiagnosticEngineRegistry

    system_intelligence_type: Final[
        Type[SystemWideIntelligence]
    ] = SystemWideIntelligence

    system_investigation_type: Final[
        Type[SystemLevelInvestigation]
    ] = SystemLevelInvestigation

    system_relationships_type: Final[
        Type[SystemProblemRelationships]
    ] = SystemProblemRelationships

    system_root_cause_type: Final[
        Type[SystemRootCauseReasoning]
    ] = SystemRootCauseReasoning

    system_recommendations_type: Final[
        Type[SystemLevelRecommendations]
    ] = SystemLevelRecommendations

    fleet_type: Final[Type[Fleet]] = Fleet

    remediation_authorization_type: Final[
        Type[RemediationAuthorization]
    ] = RemediationAuthorization


@dataclass
class V1ProductionTechnicianPlatform:
    """
    V1.0 production composition root.

    The platform owns composition and lifecycle of canonical intelligence
    components. The components themselves retain responsibility for
    their domain behavior.
    """

    fleet_name: str = "Default Fleet"

    def __post_init__(self) -> None:
        self.components = V1CanonicalComponents()

        self.diagnostic_registry = (
            self.components.diagnostic_registry_type()
        )

        self.system_intelligence = (
            self.components.system_intelligence_type()
        )

        self.system_investigation = (
            self.components.system_investigation_type()
        )

        self.system_relationships = (
            self.components.system_relationships_type()
        )

        self.system_root_cause = (
            self.components.system_root_cause_type()
        )

        self.system_recommendations = (
            self.components.system_recommendations_type()
        )

        self.fleet = self.components.fleet_type(self.fleet_name)

    def create_case(self) -> DiagnosticCase:
        """
        Create the canonical investigation container.

        V1.0 deliberately continues to use DiagnosticCase rather than
        introducing a second V1-specific case type.
        """

        return self.components.diagnostic_case_type()

    @property
    def canonical_case_type(self) -> Type[DiagnosticCase]:
        return self.components.diagnostic_case_type

    @property
    def remediation_authorization_type(
        self,
    ) -> Type[RemediationAuthorization]:
        return self.components.remediation_authorization_type


__all__ = [
    "V1CanonicalComponents",
    "V1ProductionTechnicianPlatform",
]
