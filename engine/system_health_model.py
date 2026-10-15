# ==========================================
# Windows Technician v0.9
# SYSTEM HEALTH MODEL
# ==========================================

from copy import deepcopy


class SystemHealthModel:
    """
    Builds a system-wide health state from observed
    domain findings.

    Phase 6.5 is a health interpretation layer.

    It may:
        - determine overall system health
        - calculate a bounded health score
        - preserve domain health
        - preserve finding provenance
        - report diagnostic coverage

    It must NOT:
        - infer root causes
        - claim causality
        - generate recommendations
        - authorize remediation
        - execute remediation
    """

    domain = "SYSTEM_HEALTH"

    _SEVERITY_PENALTIES = {
        "LOW": 5,
        "MEDIUM": 15,
        "WARNING": 10,
        "HIGH": 20,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    _SEVERITY_RANK = {
        "LOW": 1,
        "MEDIUM": 2,
        "WARNING": 3,
        "HIGH": 3,
        "ERROR": 4,
        "CRITICAL": 5,
    }

    def evaluate(self, domains=None):
        """
        Evaluate the health of the observed Windows system.
        """

        normalized_domains = self._normalize_domains(
            domains
        )

        if not normalized_domains:
            return {
                "status": "INCOMPLETE",
                "health_score": 0,
                "coverage": "NONE",
                "domains": [],
                "domain_health": {},
                "findings": [],
            }

        domain_names = sorted(
            normalized_domains.keys()
        )

        findings = self._collect_findings(
            normalized_domains
        )

        domain_health = self._calculate_domain_health(
            normalized_domains
        )

        status = self._calculate_system_status(
            findings
        )

        health_score = self._calculate_health_score(
            findings
        )

        coverage = self._calculate_coverage(
            domain_names
        )

        return {
            "status": status,
            "health_score": health_score,
            "coverage": coverage,
            "domains": domain_names,
            "domain_health": domain_health,
            "findings": findings,
        }

    @classmethod
    def _normalize_domains(cls, domains):
        if domains is None:
            return {}

        if not isinstance(domains, dict):
            raise ValueError(
                "System health evaluation requires "
                "a domain mapping."
            )

        normalized = {}

        for domain, payload in domains.items():
            if payload is None:
                continue

            if not isinstance(payload, dict):
                continue

            normalized_domain = str(
                domain
            ).strip().upper()

            if not normalized_domain:
                continue

            normalized[
                normalized_domain
            ] = deepcopy(payload)

        return normalized

    @classmethod
    def _collect_findings(cls, domains):
        findings = []

        for domain in sorted(domains):
            payload = domains[domain]

            domain_findings = payload.get(
                "findings"
            )

            if not isinstance(
                domain_findings,
                (list, tuple),
            ):
                continue

            for finding in domain_findings:
                if finding is None:
                    continue

                findings.append(
                    {
                        "domain": domain,
                        "finding": deepcopy(
                            finding
                        ),
                    }
                )

        return findings

    @staticmethod
    def _extract_severity(finding):
        if not isinstance(finding, dict):
            return ""
        return str(finding.get("severity", "")).strip().upper()

    @classmethod
    def _calculate_domain_health(cls, domains):
        domain_health = {}

        for domain in sorted(domains):
            payload = domains[domain]

            findings = payload.get(
                "findings"
            )

            if not isinstance(
                findings,
                (list, tuple),
            ):
                findings = []

            highest_rank = 0

            for finding in findings:
                severity = cls._extract_severity(
                    finding
                )

                rank = cls._SEVERITY_RANK.get(
                    severity,
                    0,
                )

                highest_rank = max(
                    highest_rank,
                    rank,
                )

            domain_health[domain] = (
                cls._status_from_rank(
                    highest_rank
                )
            )

        return domain_health

    @classmethod
    def _calculate_system_status(cls, findings):
        highest_rank = 0

        for item in findings:
            severity = cls._extract_severity(
                item["finding"]
            )

            rank = cls._SEVERITY_RANK.get(
                severity,
                0,
            )

            highest_rank = max(
                highest_rank,
                rank,
            )

        return cls._status_from_rank(
            highest_rank
        )

    @staticmethod
    def _status_from_rank(rank):
        if rank >= 5:
            return "CRITICAL"

        if rank >= 4:
            return "CRITICAL"

        if rank >= 3:
            return "WARNING"

        if rank >= 2:
            return "DEGRADED"

        return "HEALTHY"

    @staticmethod
    def _calculate_coverage(domain_names):
        if not domain_names:
            return "NONE"
        if len(domain_names) == 1:
            return "PARTIAL"
        return "SYSTEM_WIDE"

    @classmethod
    def _calculate_health_score(cls, findings):
        """Score unique issues using their highest observed severity."""
        issue_penalties = {}
        unidentified_penalties = []

        for item in findings:
            if not isinstance(item, dict):
                continue

            finding = item.get("finding", {})
            severity = cls._extract_severity(finding)
            penalty = cls._SEVERITY_PENALTIES.get(severity, 0)

            if not penalty:
                continue

            identity = None

            if isinstance(finding, dict):
                finding_id = finding.get("finding_id") or finding.get("id")
                finding_type = (
                    finding.get("finding_type")
                    or finding.get("category")
                    or finding.get("type")
                )
                message = finding.get("message")

                normalized_type = (
                    str(finding_type).strip().upper()
                    if finding_type
                    else ""
                )

                if normalized_type in {
                    "MEMORY_PRESSURE",
                    "MEMORY_EXHAUSTION",
                }:
                    identity = ("type", normalized_type)
                elif finding_id:
                    identity = ("id", str(finding_id).strip().casefold())
                elif finding_type:
                    identity = ("type", normalized_type)
                elif message:
                    identity = (
                        "message",
                        " ".join(str(message).split()).casefold(),
                    )

            if identity is None:
                unidentified_penalties.append(penalty)
                continue

            issue_penalties[identity] = max(
                issue_penalties.get(identity, 0),
                penalty,
            )

        total_penalty = (
            sum(issue_penalties.values())
            + sum(unidentified_penalties)
        )

        return max(0, min(100, 100 - total_penalty))
