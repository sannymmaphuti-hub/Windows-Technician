# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL INVESTIGATION
# ==========================================

from copy import deepcopy


class SystemLevelInvestigation:
    """
    Determines what the diagnostic system should investigate
    next from currently observed system evidence and patterns.

    Phase 6.7 is an investigation-planning layer.

    It may:
        - prioritize investigation targets
        - convert findings into investigation questions
        - prioritize system-wide patterns
        - preserve evidence and pattern provenance

    It must NOT:
        - claim a root cause
        - generate remediation
        - authorize changes
        - execute remediation
        - silently discard supported investigation targets
    """

    domain = "SYSTEM_INVESTIGATION"

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

    def investigate(self, system_data=None):
        """
        Construct prioritized investigation targets from
        system findings and system-wide patterns.
        """

        if system_data is None:
            system_data = {}

        if not isinstance(system_data, dict):
            raise ValueError(
                "System-level investigation requires "
                "a system-data mapping."
            )

        findings = self._normalize_findings(
            system_data.get("findings")
        )

        patterns = self._normalize_patterns(
            system_data.get("patterns")
        )

        targets = []

        for pattern in patterns:
            targets.append(
                self._build_pattern_target(
                    pattern
                )
            )

        for finding in findings:
            targets.append(
                self._build_finding_target(
                    finding
                )
            )

        targets = self._sort_targets(
            targets
        )

        return {
            "targets": targets,
            "target_count": len(targets),
        }

    @staticmethod
    def _normalize_findings(findings):
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
    def _build_pattern_target(cls, pattern):
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
            "question": (
                "What additional evidence can "
                "confirm how the observed system-wide "
                "pattern is behaving?"
            ),
        }

    @classmethod
    def _build_finding_target(cls, item):
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

        question = cls._build_question(
            item["domain"],
            finding_type,
        )

        return {
            "type": "FINDING",
            "priority": priority,
            "domain": item["domain"],
            "finding": deepcopy(
                finding
            ),
            "question": question,
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
    def _build_question(
        domain,
        finding_type,
    ):
        question_map = {
            "MEMORY_PRESSURE": (
                "What processes are contributing "
                "to the observed memory pressure?"
            ),
            "MEMORY_EXHAUSTION": (
                "What additional memory evidence "
                "can determine how severe the memory "
                "condition is?"
            ),
            "HIGH_PROCESS_MEMORY": (
                "Which process is contributing most "
                "to the observed memory condition?"
            ),
            "HIGH_COMMIT_USAGE": (
                "Which processes or resources are "
                "contributing to the high commit usage?"
            ),
            "SERVICE_FAILURE": (
                "Is the service condition contributing "
                "to other observed system problems?"
            ),
            "NETWORK_CONNECTIVITY_DEGRADED": (
                "What additional network evidence can "
                "determine the scope of the connectivity "
                "condition?"
            ),
            "PROCESS_FAILURE": (
                "What additional process evidence can "
                "determine the scope of the failure?"
            ),
        }

        return question_map.get(
            finding_type,
            (
                f"What additional {domain} evidence "
                f"can clarify the observed "
                f"{finding_type} condition?"
            ),
        )

    @classmethod
    def _sort_targets(cls, targets):
        return sorted(
            targets,
            key=lambda target: (
                -cls._PRIORITY_RANK.get(
                    target.get(
                        "priority",
                        "LOW",
                    ),
                    0,
                ),
                target.get(
                    "type",
                    "",
                ),
                target.get(
                    "domain",
                    "",
                ),
            ),
        )

