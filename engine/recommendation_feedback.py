# ==========================================
# Windows Technician v0.9
# PHASE 7.4
# RECOMMENDATION FEEDBACK
# ==========================================

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


class RecommendationFeedback:
    """
    Canonical feedback record for a recommendation
    and its later observed effect.

    Phase 7.4 records whether the intended effect
    of a recommendation was subsequently observed.

    This component is passive.

    It must NOT:
        - execute recommendations
        - authorize remediation
        - perform remediation
        - generate new recommendations
        - modify diagnostic history
        - modify root-cause candidates
        - automatically change intelligence confidence
        - create learning signals
    """

    _OUTCOMES = {
        "CONFIRMED",
        "PARTIAL",
        "REFUTED",
        "UNKNOWN",
    }

    def __init__(
        self,
        case_id,
        machine_id,
        recommendation_id,
        recommendation,
        expected_effect,
        observed_effect=None,
        outcome="UNKNOWN",
        metadata=None,
    ):
        self.case_id = self._require_identifier(
            case_id,
            "case_id",
        ).upper()

        self.machine_id = self._require_identifier(
            machine_id,
            "machine_id",
        ).upper()

        self.recommendation_id = (
            self._require_identifier(
                recommendation_id,
                "recommendation_id",
            ).upper()
        )

        if recommendation is None:
            raise ValueError(
                "recommendation is required."
            )

        if expected_effect is None:
            raise ValueError(
                "expected_effect is required."
            )

        self.recommendation = deepcopy(
            recommendation
        )

        self.expected_effect = deepcopy(
            expected_effect
        )

        self.observed_effect = deepcopy(
            observed_effect
        )

        self.outcome = self._normalize_outcome(
            outcome
        )

        self.metadata = deepcopy(
            metadata
            if isinstance(metadata, dict)
            else {}
        )

        self.feedback_id = str(
            uuid4()
        )

        self.timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    @staticmethod
    def _require_identifier(
        value,
        field_name,
    ):
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{field_name} must be "
                "a non-empty string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must be "
                "a non-empty string."
            )

        return normalized

    @classmethod
    def _normalize_outcome(
        cls,
        outcome,
    ):
        if not isinstance(
            outcome,
            str,
        ):
            raise ValueError(
                "outcome must be "
                "a supported string value."
            )

        normalized = outcome.strip().upper()

        if normalized not in cls._OUTCOMES:
            raise ValueError(
                f"Unsupported outcome: "
                f"{outcome!r}."
            )

        return normalized

    def to_dict(self):
        return {
            "feedback_id": self.feedback_id,
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "recommendation_id": (
                self.recommendation_id
            ),
            "recommendation": deepcopy(
                self.recommendation
            ),
            "expected_effect": deepcopy(
                self.expected_effect
            ),
            "observed_effect": deepcopy(
                self.observed_effect
            ),
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "metadata": deepcopy(
                self.metadata
            ),
        }

