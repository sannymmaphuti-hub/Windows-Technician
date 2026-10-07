# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL RECOMMENDATIONS
# ==========================================

from copy import deepcopy


class SystemLevelRecommendations:
    """
    Produces system-level recommendations from observed
    findings and system-wide patterns.

    Phase 6.8 is a recommendation-intelligence layer.

    It may:
        - translate findings into useful next actions
        - translate system-wide patterns into broader
          investigation recommendations
        - prioritize recommendations
        - preserve evidence provenance
        - preserve pattern provenance

    It must NOT:
        - claim a root cause
        - claim unsupported certainty
        - authorize remediation
        - execute remediation
        - silently discard supported recommendations

    The recommendation layer answers:

        "Given what we currently know, what should
         the technician or user do next?"

    It does NOT answer:

        "What should the system automatically change?"
    """

    domain = "SYSTEM_RECOMMENDATIONS"

    _SEVERITY_PRIORITY = {
        "CRITICAL": "HIGH",
        "ERROR": "HIGH",
        "WARNING": "MEDIUM",
        "HIGH": "MEDIUM",
        "MEDIUM": "MEDIUM",
        "LOW": "LOW",
    }

    _PRIORITY_RANK = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
    }

    def generate(self, system_data=None):
        """
        Generate prioritized recommendations from
        system findings and system-wide patterns.
        """

        if system_data is None:
            system_data = {}

        if not isinstance(system_data, dict):
            raise ValueError(
                "System-level recommendations require "
                "a system-data mapping."
            )

        findings = self._normalize_findings(
            system_data.get("findings")
        )

        patterns = self._normalize_patterns(
            system_data.get("patterns")
        )

        recommendations = []

        for pattern in patterns:
            recommendation = (
                self._build_pattern_recommendation(
                    pattern
                )
            )

            if recommendation is not None:
                recommendations.append(
                    recommendation
                )

        for finding in findings:
            recommendation = (
                self._build_finding_recommendation(
                    finding
                )
            )

            if recommendation is not None:
                recommendations.append(
                    recommendation
                )

        recommendations = self._sort_recommendations(
            recommendations
        )

        return {
            "recommendations": recommendations,
            "recommendation_count": len(
                recommendations
            ),
        }

    @staticmethod
    def _normalize_findings(findings):
        """
        Normalize valid cross-domain findings while
        preserving the original finding data.
        """

        if not isinstance(
            findings,
            (list, tuple),
        ):
            return []

        normalized = []

        for item in findings:
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

            normalized.append(
                {
                    "domain": domain,
                    "finding": deepcopy(
                        finding
                    ),
                }
            )

        return normalized

    @staticmethod
    def _normalize_patterns(patterns):
        """
        Normalize valid system-wide patterns while
        preserving their provenance.
        """

        if not isinstance(
            patterns,
            (list, tuple),
        ):
            return []

        normalized = []

        for pattern in patterns:
            if not isinstance(pattern, dict):
                continue

            pattern_type = str(
                pattern.get(
                    "type",
                    "",
                )
            ).strip().upper()

            if not pattern_type:
                continue

            normalized_pattern = deepcopy(
                pattern
            )

            normalized_pattern["type"] = (
                pattern_type
            )

            domains = normalized_pattern.get(
                "domains",
                [],
            )

            if isinstance(
                domains,
                (list, tuple),
            ):
                normalized_pattern["domains"] = sorted(
                    {
                        str(domain)
                        .strip()
                        .upper()
                        for domain in domains
                        if str(domain).strip()
                    }
                )
            else:
                normalized_pattern["domains"] = []

            normalized.append(
                normalized_pattern
            )

        return normalized

    @classmethod
    def _build_finding_recommendation(
        cls,
        item,
    ):
        finding = item["finding"]

        severity = cls._extract_severity(
            finding
        )

        priority = cls._SEVERITY_PRIORITY.get(
            severity,
            "LOW",
        )

        finding_type = str(
            finding.get(
                "finding_type",
                "UNKNOWN",
            )
        ).strip().upper()

        action = cls._build_action(
            item["domain"],
            finding_type,
        )

        rationale = cls._build_rationale(
            item["domain"],
            finding_type,
            severity,
        )

        return {
            "type": "FINDING",
            "priority": priority,
            "domain": item["domain"],
            "finding": deepcopy(
                finding
            ),
            "action": action,
            "rationale": rationale,
        }

    @classmethod
    def _build_pattern_recommendation(
        cls,
        pattern,
    ):
        pattern_type = pattern.get(
            "type",
            "",
        )

        action, rationale = (
            cls._build_pattern_action(
                pattern_type
            )
        )

        return {
            "type": "SYSTEM_PATTERN",
            "priority": "HIGH",
            "domains": deepcopy(
                pattern.get(
                    "domains",
                    [],
                )
            ),
            "pattern": deepcopy(
                pattern
            ),
            "action": action,
            "rationale": rationale,
        }

    @staticmethod
    def _extract_severity(finding):
        return str(
            finding.get(
                "severity",
                "",
            )
        ).strip().upper()

    @staticmethod
    def _build_action(
        domain,
        finding_type,
    ):
        actions = {
            "MEMORY_PRESSURE": (
                "Review memory usage and identify "
                "the processes contributing to the "
                "observed memory pressure."
            ),
            "MEMORY_EXHAUSTION": (
                "Investigate memory consumption and "
                "determine whether additional memory "
                "evidence is needed."
            ),
            "HIGH_PROCESS_MEMORY": (
                "Review the processes using significant "
                "memory and identify which process is "
                "contributing most to the condition."
            ),
            "HIGH_COMMIT_USAGE": (
                "Review process and system resource "
                "usage to identify contributors to "
                "the high commit condition."
            ),
            "SERVICE_FAILURE": (
                "Review the affected service and "
                "investigate whether its condition "
                "is contributing to other system "
                "problems."
            ),
            "NETWORK_CONNECTIVITY_DEGRADED": (
                "Review network connectivity and "
                "investigate the scope of the "
                "observed network condition."
            ),
            "PROCESS_FAILURE": (
                "Review the affected process and "
                "collect additional evidence about "
                "the failure."
            ),
            "SYSTEM_FAILURE": (
                "Review the system condition and "
                "collect additional evidence before "
                "taking corrective action."
            ),
        }

        return actions.get(
            finding_type,
            (
                f"Review the observed {domain} "
                f"condition and collect additional "
                f"evidence before taking corrective "
                f"action."
            ),
        )

    @staticmethod
    def _build_rationale(
        domain,
        finding_type,
        severity,
    ):
        severity_text = (
            severity.lower()
            if severity
            else "observed"
        )

        return (
            f"The {domain} domain reported a "
            f"{severity_text} {finding_type} condition. "
            "Additional evidence should be reviewed "
            "before determining the appropriate "
            "corrective action."
        )

    @staticmethod
    def _build_pattern_action(
        pattern_type,
    ):
        pattern_actions = {
            "SYSTEM_RESOURCE_PRESSURE": (
                "Investigate the interaction between "
                "system resource pressure and the "
                "processes contributing to it before "
                "selecting corrective action.",
                (
                    "The system-wide evidence shows a "
                    "resource-pressure pattern across "
                    "multiple domains. The relationship "
                    "should be investigated further rather "
                    "than treated as proof of a single cause."
                ),
            ),
            "SERVICE_NETWORK_DEGRADATION": (
                "Investigate the affected service and "
                "network conditions together to determine "
                "the scope of the degradation.",
                (
                    "The evidence shows related service "
                    "and network conditions across multiple "
                    "domains. Further investigation can "
                    "determine whether the conditions are "
                    "connected."
                ),
            ),
        }

        return pattern_actions.get(
            pattern_type,
            (
                "Investigate the system-wide pattern "
                "and collect additional evidence before "
                "selecting corrective action.",
                (
                    "A system-wide pattern was detected "
                    "across the available evidence. "
                    "Further investigation is required "
                    "before drawing a causal conclusion."
                ),
            ),
        )

    @classmethod
    def _sort_recommendations(
        cls,
        recommendations,
    ):
        return sorted(
            recommendations,
            key=lambda recommendation: (
                -cls._PRIORITY_RANK.get(
                    recommendation.get(
                        "priority",
                        "LOW",
                    ),
                    0,
                ),
                recommendation.get(
                    "type",
                    "",
                ),
                recommendation.get(
                    "domain",
                    "",
                ),
            ),
        )


