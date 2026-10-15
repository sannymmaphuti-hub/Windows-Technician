# ==========================================
# Windows Technician v0.9
# SYSTEM PROBLEM RELATIONSHIPS
# ==========================================

from copy import deepcopy


class SystemProblemRelationships:
    """
    Identifies evidence-supported relationships between
    problems reported by different Windows diagnostic domains.

    Phase 6.3 is a relationship layer.

    It may:
        - group related findings
        - identify cross-domain interactions
        - preserve evidence provenance
        - assign relationship confidence

    It must NOT:
        - claim causality
        - select a root cause
        - generate remediation
        - execute remediation
        - replace domain diagnostics
    """

    domain = "SYSTEM_RELATIONSHIPS"

    def analyze(self, evidence):
        if not isinstance(evidence, list):
            raise ValueError(
                "System problem relationships require "
                "a list of evidence."
            )

        normalized = self._normalize_evidence(
            evidence
        )

        relationships = []

        memory_process = (
            self._find_memory_process_relationship(
                normalized
            )
        )

        if memory_process is not None:
            relationships.append(
                memory_process
            )

        return {
            "relationships": relationships,
            "relationship_count": len(
                relationships
            ),
            "root_causes": [],
            "primary_root_cause": None,
        }

    @staticmethod
    def _normalize_evidence(evidence):
        normalized = []

        for item in evidence:
            if not isinstance(item, dict):
                continue

            domain = str(
                item.get(
                    "domain",
                    "",
                )
            ).strip().upper()

            if not domain:
                continue

            if "finding" not in item:
                continue

            finding = item["finding"]

            if finding is None:
                continue

            normalized.append(
                {
                    "domain": domain,
                    "finding": deepcopy(
                        finding
                    ),
                }
            )

        return normalized

    @classmethod
    def _finding_type(cls, finding):
        """
        Extract a canonical finding type from both
        legacy string findings and current structured
        finding dictionaries.
        """

        if isinstance(finding, str):
            return finding.strip().upper()

        if isinstance(finding, dict):
            return str(
                finding.get(
                    "finding_type",
                    "",
                )
            ).strip().upper()

        return ""

    @classmethod
    def _find_memory_process_relationship(
        cls,
        evidence,
    ):
        """
        Detect the known resource interaction:

            MEMORY_PRESSURE
                    +
            HIGH_PROCESS_MEMORY / HIGH_COMMIT_USAGE

        The relationship is evidence-supported but
        does not establish causality.
        """

        memory_evidence = [
            item
            for item in evidence
            if item["domain"] == "MEMORY"
            and cls._finding_type(
                item["finding"]
            )
            == "MEMORY_PRESSURE"
        ]

        process_evidence = [
            item
            for item in evidence
            if item["domain"] == "PROCESS"
            and cls._finding_type(
                item["finding"]
            )
            in {
                "HIGH_PROCESS_MEMORY",
                "HIGH_COMMIT_USAGE",
            }
        ]

        if not memory_evidence:
            return None

        if not process_evidence:
            return None

        selected = [
            *memory_evidence,
            *process_evidence,
        ]

        unique_evidence = []

        for item in selected:
            if item in unique_evidence:
                continue

            unique_evidence.append(
                item
            )

        domains = sorted(
            {
                item["domain"]
                for item in unique_evidence
            }
        )

        findings = [
            deepcopy(
                item["finding"]
            )
            for item in unique_evidence
        ]

        return {
            "type": "RESOURCE_INTERACTION",
            "confidence": "MEDIUM",
            "domains": domains,
            "findings": findings,
            "evidence": deepcopy(
                unique_evidence
            ),
        }
