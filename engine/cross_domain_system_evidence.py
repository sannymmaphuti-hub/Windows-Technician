# ==========================================
# Windows Technician v0.9
# CROSS-DOMAIN SYSTEM EVIDENCE
# ==========================================

from copy import deepcopy


class CrossDomainSystemEvidence:
    """
    Constructs a system-wide evidence surface from
    independent Windows diagnostic domains.

    Phase 6.2 is deliberately evidence-only.

    It may:
        - collect findings from multiple domains
        - preserve domain provenance
        - preserve original domain context
        - expose evidence to later reasoning layers

    It must NOT:
        - infer relationships
        - infer causality
        - determine root causes
        - generate recommendations
        - authorize remediation
        - execute remediation
    """

    domain = "SYSTEM_WIDE_EVIDENCE"

    def collect(self, domains=None):
        """
        Collect cross-domain evidence.

        Parameters
        ----------
        domains:
            Mapping of domain name -> diagnostic payload.
        """

        normalized_domains = self._normalize_domains(
            domains
        )

        domain_names = sorted(
            normalized_domains.keys()
        )

        evidence = self._collect_findings(
            normalized_domains
        )

        return {
            "evidence": evidence,
            "evidence_count": len(evidence),
            "domains": domain_names,
            "domain_context": deepcopy(
                normalized_domains
            ),

            # Reserved for Phase 6.3.
            "relationships": [],

            # Reserved for Phase 6.4.
            "root_causes": [],
            "primary_root_cause": None,
        }

    # ==========================================
    # DOMAIN NORMALIZATION
    # ==========================================

    @staticmethod
    def _normalize_domains(domains):
        """
        Normalize valid diagnostic domain payloads.

        Invalid or incomplete domain payloads are ignored
        rather than converted into fabricated evidence.
        """

        if domains is None:
            return {}

        if not isinstance(domains, dict):
            raise ValueError(
                "Cross-domain system evidence requires "
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

    # ==========================================
    # EVIDENCE COLLECTION
    # ==========================================

    @staticmethod
    def _collect_findings(domains):
        """
        Convert domain findings into system-level evidence
        while retaining their originating domain.

        No interpretation occurs here.
        """

        evidence = []

        for domain in sorted(domains):

            payload = domains[domain]

            findings = payload.get(
                "findings"
            )

            if not isinstance(
                findings,
                (list, tuple),
            ):
                continue

            for finding in findings:

                evidence.append(
                    {
                        "domain": domain,
                        "finding": deepcopy(
                            finding
                        ),
                    }
                )

        return evidence

