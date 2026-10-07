# ==========================================
# Windows Technician v0.9
# SYSTEM-LEVEL ROOT-CAUSE REASONING
# ==========================================

from copy import deepcopy


class SystemRootCauseReasoning:
    """
    Produces evidence-supported root-cause candidates from
    system-level relationships.

    Phase 6.4 is a reasoning layer.

    It may:
        - construct root-cause candidates
        - preserve supporting relationships
        - calculate candidate confidence
        - select the strongest supported candidate

    It must NOT:
        - claim absolute certainty
        - invent unsupported causes
        - discard alternative candidates
        - generate remediation
        - execute remediation
    """

    domain = "SYSTEM_ROOT_CAUSE"

    def analyze(self, relationships):
        """
        Analyze system relationships and construct root-cause
        candidates.
        """

        if not isinstance(relationships, list):
            raise ValueError(
                "System root-cause reasoning requires "
                "a list of relationships."
            )

        normalized = self._normalize_relationships(
            relationships
        )

        candidates = []

        for relationship in normalized:
            candidate = self._build_candidate(
                relationship
            )

            if candidate is None:
                continue

            candidates.append(candidate)

        primary = self._select_primary(
            candidates
        )

        return {
            "root_causes": candidates,
            "primary_root_cause": primary,
            "confidence": (
                primary["confidence"]
                if primary is not None
                else "NONE"
            ),
        }

    # ==========================================
    # RELATIONSHIP NORMALIZATION
    # ==========================================

    @staticmethod
    def _normalize_relationships(relationships):
        """
        Preserve valid relationships while ignoring malformed
        relationship objects.
        """

        normalized = []

        for relationship in relationships:
            if not isinstance(relationship, dict):
                continue

            relationship_type = str(
                relationship.get(
                    "type",
                    "",
                )
            ).strip().upper()

            if not relationship_type:
                continue

            normalized_relationship = deepcopy(
                relationship
            )

            normalized_relationship["type"] = (
                relationship_type
            )

            normalized.append(
                normalized_relationship
            )

        return normalized

    # ==========================================
    # CANDIDATE CONSTRUCTION
    # ==========================================

    @classmethod
    def _build_candidate(cls, relationship):
        """
        Convert a supported relationship into a root-cause
        candidate.

        Each supported relationship is allowed to produce
        its own hypothesis. Alternatives are preserved.
        """

        relationship_type = relationship["type"]

        if relationship_type == (
            "RESOURCE_INTERACTION"
        ):
            return cls._resource_candidate(
                relationship
            )

        if relationship_type == (
            "SERVICE_INTERACTION"
        ):
            return cls._service_candidate(
                relationship
            )

        return None

    # ==========================================
    # RESOURCE CANDIDATE
    # ==========================================

    @staticmethod
    def _resource_candidate(relationship):
        """
        Construct a resource-consumption hypothesis.
        """

        confidence = (
            SystemRootCauseReasoning
            ._normalize_confidence(
                relationship.get(
                    "confidence",
                    "NONE",
                )
            )
        )

        return {
            "cause_type": (
                "PROCESS_RESOURCE_CONSUMPTION"
            ),
            "confidence": confidence,
            "explanation": (
                "Process resource consumption is a "
                "candidate explanation for the observed "
                "memory pressure and process-memory "
                "relationship."
            ),
            "supporting_relationships": [
                deepcopy(relationship)
            ],
        }

    # ==========================================
    # SERVICE CANDIDATE
    # ==========================================

    @staticmethod
    def _service_candidate(relationship):
        """
        Construct a service-related hypothesis.

        This remains a candidate explanation rather than
        a confirmed causal conclusion.
        """

        confidence = (
            SystemRootCauseReasoning
            ._normalize_confidence(
                relationship.get(
                    "confidence",
                    "NONE",
                )
            )
        )

        return {
            "cause_type": (
                "SERVICE_NETWORK_INTERACTION"
            ),
            "confidence": confidence,
            "explanation": (
                "A service-related condition is a "
                "candidate explanation for the observed "
                "service and network relationship."
            ),
            "supporting_relationships": [
                deepcopy(relationship)
            ],
        }

    # ==========================================
    # CONFIDENCE
    # ==========================================

    @staticmethod
    def _normalize_confidence(confidence):
        """
        Preserve the confidence supplied by the relationship
        layer without upgrading it.
        """

        normalized = str(
            confidence
        ).strip().upper()

        if normalized in {
            "LOW",
            "MEDIUM",
            "HIGH",
        }:
            return normalized

        return "LOW"

    # ==========================================
    # PRIMARY CANDIDATE SELECTION
    # ==========================================

    @staticmethod
    def _select_primary(candidates):
        """
        Select the strongest currently supported candidate.

        Confidence ranking:

            HIGH > MEDIUM > LOW

        Ties preserve discovery order.

        No candidate is upgraded beyond the evidence
        supplied by the relationship layer.
        """

        if not candidates:
            return None

        confidence_rank = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
        }

        return max(
            candidates,
            key=lambda candidate: confidence_rank.get(
                candidate.get(
                    "confidence",
                    "LOW",
                ),
                0,
            ),
        )

