# ==========================================
# Windows Technician v0.9
# SYSTEM-WIDE INTELLIGENCE ARCHITECTURE
# ==========================================

from copy import deepcopy


class SystemWideIntelligence:
    """
    Canonical system-wide intelligence boundary.

    Phase 6.1 is responsible for constructing a stable,
    system-level representation of available diagnostic
    intelligence.

    It deliberately does NOT:
        - infer root causes
        - make remediation decisions
        - generate recommendations
        - replace domain intelligence
        - claim causality from correlation

    Those responsibilities belong to later Phase 6 layers.
    """

    domain = "SYSTEM_WIDE"

    def analyze(self, domains=None):
        """
        Construct a system-wide intelligence context.

        Parameters
        ----------
        domains:
            Mapping of domain name -> diagnostic payload.

        Example:

            {
                "MEMORY": {
                    "findings": [...]
                },
                "PROCESS": {
                    "findings": [...]
                }
            }

        The input is treated as diagnostic evidence/context.
        It is preserved without allowing this layer to make
        unsupported causal claims.
        """

        normalized_domains = self._normalize_domains(
            domains
        )

        domain_names = sorted(
            normalized_domains.keys()
        )

        domain_count = len(domain_names)

        status = self._determine_status(
            domain_count
        )

        return {
            "status": status,
            "domain_count": domain_count,
            "domains": domain_names,

            # Preserve the complete domain intelligence.
            "domain_data": deepcopy(
                normalized_domains
            ),

            # Preserve the complete domain payloads here too.
            #
            # Phase 6.1 must retain domain context and provenance.
            # Cross-domain interpretation belongs to later phases.
            "domain_findings": deepcopy(
                normalized_domains
            ),

            # Phase 6.1 establishes the relationship
            # surface but does not infer relationships yet.
            "relationships": [],

            # System-level findings are reserved for
            # evidence-supported system reasoning.
            "system_findings": [],

            # Root-cause reasoning belongs to Phase 6.4.
            "root_causes": [],
            "primary_root_cause": None,
            "root_cause_confidence": "NONE",

            # Recommendations belong to Phase 6.8.
            "recommendations": [],

            # Remediation is explicitly outside this layer.
            "remediation": None,
        }

    # ==========================================
    # DOMAIN NORMALIZATION
    # ==========================================

    @staticmethod
    def _normalize_domains(domains):
        """
        Normalize the supplied domain mapping without
        inventing missing diagnostic information.
        """

        if domains is None:
            return {}

        if not isinstance(domains, dict):
            raise ValueError(
                "System-wide intelligence requires "
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
    # SYSTEM COMPLETENESS
    # ==========================================

    @staticmethod
    def _determine_status(domain_count):
        """
        Describe how much system information is currently
        available.

        This is an availability state, not a health judgement.
        """

        if domain_count == 0:
            return "INCOMPLETE"

        if domain_count == 1:
            return "PARTIAL"

        return "ACTIVE"