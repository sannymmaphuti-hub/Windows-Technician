from __future__ import annotations

from typing import Any

from engine.diagnostic_case import DiagnosticCase
from engine.system_level_investigation import SystemLevelInvestigation
from engine.system_level_recommendations import SystemLevelRecommendations
from engine.system_problem_relationships import SystemProblemRelationships
from engine.system_root_cause_reasoning import SystemRootCauseReasoning
from engine.system_wide_intelligence import SystemWideIntelligence


class V1InvestigationPipeline:
    """
    V1.0 orchestration boundary for system investigation.

    This class does not implement diagnostic intelligence itself.
    It composes the existing canonical V0.9 intelligence engines
    into one investigation flow.
    """

    def __init__(
        self,
        system_intelligence: SystemWideIntelligence | None = None,
        investigation: SystemLevelInvestigation | None = None,
        relationships: SystemProblemRelationships | None = None,
        root_cause: SystemRootCauseReasoning | None = None,
        recommendations: SystemLevelRecommendations | None = None,
    ) -> None:
        self.system_intelligence = (
            system_intelligence
            if system_intelligence is not None
            else SystemWideIntelligence()
        )

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

        self.root_cause = (
            root_cause
            if root_cause is not None
            else SystemRootCauseReasoning()
        )

        self.recommendations = (
            recommendations
            if recommendations is not None
            else SystemLevelRecommendations()
        )

    def run(
        self,
        domains: dict[str, Any] | None = None,
        system_data: dict[str, Any] | None = None,
        evidence: list[Any] | None = None,
        case: DiagnosticCase | None = None,
    ) -> dict[str, Any]:
        """
        Execute the canonical V1.0 investigation sequence.

        Parameters
        ----------
        domains:
            Domain-level diagnostic context consumed by
            SystemWideIntelligence.

        system_data:
            System-level findings/patterns consumed by investigation
            and recommendation intelligence.

        evidence:
            Normalized evidence consumed by relationship analysis.

        case:
            Optional existing DiagnosticCase to populate.

        Returns
        -------
        dict
            Complete V1.0 investigation result containing the
            outputs of every canonical stage and the resulting case.
        """

        system_context = self.system_intelligence.analyze(
            domains
        )

        normalized_system_data = (
            system_data
            if system_data is not None
            else {}
        )

        investigation_result = self.investigation.investigate(
            normalized_system_data
        )

        evidence_input = (
            evidence
            if evidence is not None
            else []
        )

        # SystemProblemRelationships requires wrapped evidence:
        # {"domain": "...", "finding": {...}}.
        # Normalize the nested finding without discarding provenance.
        relationship_evidence = []

        for item in evidence_input:
            if (
                isinstance(item, dict)
                and isinstance(item.get("finding"), dict)
            ):
                normalized_finding = dict(item["finding"])

                # Normalize known legacy memory findings only when
                # a canonical finding type was not already supplied.
                existing_type = normalized_finding.get("finding_type")
                category = normalized_finding.get("category")

                if (
                    not existing_type
                    and isinstance(category, str)
                    and category.strip().upper() == "MEMORY"
                ):
                    normalized_finding["finding_type"] = "MEMORY_PRESSURE"

                normalized_item = dict(item)
                normalized_item["finding"] = normalized_finding
                relationship_evidence.append(normalized_item)
            else:
                relationship_evidence.append(item)

        relationship_result = self.relationships.analyze(
            relationship_evidence
        )

        relationship_items = relationship_result.get(
            "relationships",
            [],
        )

        root_cause_result = self.root_cause.analyze(
            relationship_items
        )

        # Merge relationship evidence and system-data findings for recommendations.
        # Keep caller-owned data unchanged and preserve distinct evidence.
        recommendation_system_data = dict(normalized_system_data)
        recommendation_findings = []
        seen_recommendation_findings = set()

        for source in (
            relationship_evidence,
            normalized_system_data.get("findings", []),
        ):
            if not isinstance(source, (list, tuple)):
                continue

            for item in source:
                if not isinstance(item, dict):
                    continue

                finding = item.get("finding")
                domain = str(item.get("domain", "")).strip().upper()

                if not domain or not isinstance(finding, dict):
                    continue

                identity = (
                    domain,
                    repr(sorted(
                        finding.items(),
                        key=lambda pair: str(pair[0]),
                    )),
                )

                if identity in seen_recommendation_findings:
                    continue

                seen_recommendation_findings.add(identity)
                recommendation_findings.append(item)

        recommendation_system_data["findings"] = recommendation_findings
        recommendation_result = self.recommendations.generate(
            recommendation_system_data
        )

        diagnostic_case = (
            case
            if case is not None
            else DiagnosticCase()
        )

        diagnostic_case.set_evidence(
            evidence_input
        )

        diagnostic_case.set_findings(
            normalized_system_data.get(
                "findings",
                [],
            )
        )

        diagnostic_case.set_correlations(
            relationship_items
        )

        diagnostic_case.set_root_causes(
            root_cause_result.get(
                "root_causes",
                [],
            )
        )

        diagnostic_case.set_primary_root_cause(
            root_cause_result.get(
                "primary_root_cause"
            )
        )

        diagnostic_case.set_recommendations(
            recommendation_result.get(
                "recommendations",
                [],
            )
        )

        return {
            "case": diagnostic_case,
            "system_intelligence": system_context,
            "investigation": investigation_result,
            "relationships": relationship_result,
            "root_cause": root_cause_result,
            "recommendations": recommendation_result,
        }


__all__ = [
    "V1InvestigationPipeline",
]
