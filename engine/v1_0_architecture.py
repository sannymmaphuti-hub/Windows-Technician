from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class V1ArchitectureLayer(str, Enum):
    """Canonical production-platform layers."""

    CAPABILITY = "capability"
    EVIDENCE = "evidence"
    INTELLIGENCE = "intelligence"
    INVESTIGATION = "investigation"
    CASE = "case"
    DECISION = "decision"
    REMEDIATION = "remediation"
    VERIFICATION = "verification"
    HISTORY = "history"


class V1ArchitectureBoundary(str, Enum):
    """Responsibilities that must remain separated."""

    UI_PRESENTATION = "ui_presentation"
    DIAGNOSTIC_COLLECTION = "diagnostic_collection"
    SYSTEM_INTELLIGENCE = "system_intelligence"
    INVESTIGATION = "investigation"
    CASE_MANAGEMENT = "case_management"
    AUTHORIZATION = "authorization"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    HISTORY = "history"


@dataclass(frozen=True)
class V1ArchitectureDefinition:
    """
    Canonical V1.0 Production Technician Platform architecture.

    This is intentionally declarative.

    It defines what the platform is allowed to consider canonical
    without implementing another diagnostic or remediation engine.
    """

    name: Final[str] = "Windows Technician V1.0"
    product_type: Final[str] = "production_technician_platform"
    architecture_version: Final[str] = "1.0"

    layers: tuple[V1ArchitectureLayer, ...] = (
        V1ArchitectureLayer.CAPABILITY,
        V1ArchitectureLayer.EVIDENCE,
        V1ArchitectureLayer.INTELLIGENCE,
        V1ArchitectureLayer.INVESTIGATION,
        V1ArchitectureLayer.CASE,
        V1ArchitectureLayer.DECISION,
        V1ArchitectureLayer.REMEDIATION,
        V1ArchitectureLayer.VERIFICATION,
        V1ArchitectureLayer.HISTORY,
    )

    boundaries: tuple[V1ArchitectureBoundary, ...] = (
        V1ArchitectureBoundary.UI_PRESENTATION,
        V1ArchitectureBoundary.DIAGNOSTIC_COLLECTION,
        V1ArchitectureBoundary.SYSTEM_INTELLIGENCE,
        V1ArchitectureBoundary.INVESTIGATION,
        V1ArchitectureBoundary.CASE_MANAGEMENT,
        V1ArchitectureBoundary.AUTHORIZATION,
        V1ArchitectureBoundary.EXECUTION,
        V1ArchitectureBoundary.VERIFICATION,
        V1ArchitectureBoundary.HISTORY,
    )

    canonical_case_type: Final[str] = "DiagnosticCase"

    intelligence_inputs: tuple[str, ...] = (
        "observations",
        "signals",
        "evidence",
        "correlations",
        "historical_context",
        "fleet_context",
    )

    intelligence_outputs: tuple[str, ...] = (
        "findings",
        "relationships",
        "root_causes",
        "explanations",
        "recommendations",
    )

    remediation_chain: tuple[str, ...] = (
        "eligibility",
        "decision",
        "authorization",
        "execution",
        "verification",
        "recovery",
    )

    @property
    def ui_must_not_decide(self) -> bool:
        return True

    @property
    def intelligence_must_not_execute(self) -> bool:
        return True

    @property
    def recommendation_is_not_authorization(self) -> bool:
        return True

    @property
    def execution_is_not_verification(self) -> bool:
        return True

    @property
    def failure_is_not_retry_authorization(self) -> bool:
        return True

    @property
    def case_is_canonical_investigation_container(self) -> bool:
        return True


V1_ARCHITECTURE: Final[V1ArchitectureDefinition] = (
    V1ArchitectureDefinition()
)


__all__ = [
    "V1ArchitectureBoundary",
    "V1ArchitectureDefinition",
    "V1ArchitectureLayer",
    "V1_ARCHITECTURE",
]
