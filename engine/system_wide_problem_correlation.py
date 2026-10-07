# ==========================================
# Windows Technician v0.9
# SYSTEM-WIDE PROBLEM CORRELATION
# ==========================================

from copy import deepcopy


class SystemWideProblemCorrelation:
    """
    Identifies broader system-level problem patterns from
    cross-domain findings.

    Phase 6.6 is a correlation layer.

    It may:
        - identify recurring cross-domain problem patterns
        - group related findings
        - preserve evidence provenance
        - preserve domain relationships
        - assign correlation confidence

    It must NOT:
        - claim causality
        - select a root cause
        - generate recommendations
        - authorize remediation
        - execute remediation
    """

    domain = "SYSTEM_WIDE_CORRELATION"

    def analyze(self, evidence):
        if not isinstance(evidence, list):
            raise ValueError(
                "System-wide problem correlation requires "
                "a list of evidence."
            )

        normalized = self._normalize_evidence(
            evidence
        )

        patterns = []

        resource_pattern = (
            self._build_resource_pattern(
                normalized
            )
        )

        if resource_pattern is not None:
            patterns.append(
                resource_pattern
            )

        service_pattern = (
            self._build_service_network_pattern(
                normalized
            )
        )

        if service_pattern is not None:
            patterns.append(
                service_pattern
            )

        return {
            "patterns": patterns,
            "pattern_count": len(patterns),
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

            if not isinstance(finding, dict):
                continue

            finding_type = str(
                finding.get(
                    "finding_type",
                    "",
                )
            ).strip().upper()

            if not finding_type:
                continue

            normalized_finding = deepcopy(
                finding
            )

            normalized_finding[
                "finding_type"
            ] = finding_type

            normalized.append(
                {
                    "domain": domain,
                    "finding": normalized_finding,
                }
            )

        return normalized

    @classmethod
    def _build_resource_pattern(cls, evidence):
        memory_items = cls._matching_evidence(
            evidence,
            "MEMORY",
            {
                "MEMORY_PRESSURE",
            },
        )

        process_items = cls._matching_evidence(
            evidence,
            "PROCESS",
            {
                "HIGH_PROCESS_MEMORY",
                "HIGH_COMMIT_USAGE",
            },
        )

        if not memory_items or not process_items:
            return None

        selected = cls._unique_evidence(
            memory_items[:1]
            + process_items
        )

        return {
            "type": "SYSTEM_RESOURCE_PRESSURE",
            "confidence": "MEDIUM",
            "domains": sorted(
                {
                    item["domain"]
                    for item in selected
                }
            ),
            "findings": [
                deepcopy(
                    item["finding"]
                )
                for item in selected
            ],
            "evidence": deepcopy(
                selected
            ),
        }

    @classmethod
    def _build_service_network_pattern(
        cls,
        evidence,
    ):
        service_items = cls._matching_evidence(
            evidence,
            "SERVICE",
            {
                "SERVICE_FAILURE",
            },
        )

        network_items = cls._matching_evidence(
            evidence,
            "NETWORK",
            {
                "NETWORK_CONNECTIVITY_DEGRADED",
            },
        )

        if not service_items or not network_items:
            return None

        selected = cls._unique_evidence(
            service_items
            + network_items
        )

        return {
            "type": (
                "SERVICE_NETWORK_DEGRADATION"
            ),
            "confidence": "MEDIUM",
            "domains": sorted(
                {
                    item["domain"]
                    for item in selected
                }
            ),
            "findings": [
                deepcopy(
                    item["finding"]
                )
                for item in selected
            ],
            "evidence": deepcopy(
                selected
            ),
        }

    @staticmethod
    def _matching_evidence(
        evidence,
        domain,
        finding_types,
    ):
        return [
            item
            for item in evidence
            if item["domain"] == domain
            and item["finding"].get(
                "finding_type"
            ) in finding_types
        ]

    @staticmethod
    def _unique_evidence(evidence):
        unique = []

        for item in evidence:
            if item in unique:
                continue

            unique.append(
                deepcopy(item)
            )

        return unique

