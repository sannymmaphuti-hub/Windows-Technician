# ==========================================
# Windows Technician v0.9
# PHASE 7.1
# INTELLIGENCE FEEDBACK ARCHITECTURE
# ==========================================

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


class IntelligenceFeedback:
    """
    Canonical feedback record for Windows Technician.

    Phase 7.1 records the relationship between an
    intelligence event and its later observed outcome.

    This class is intentionally passive.

    It must NOT:
        - modify diagnostic history
        - change root-cause candidates
        - change confidence automatically
        - generate recommendations
        - authorize remediation
        - execute remediation
        - learn from feedback

    Later Phase 7 layers may consume these records.
    """

    _OUTCOMES = {
        "CONFIRMED",
        "PARTIAL",
        "REFUTED",
        "UNKNOWN",
    }

    _CONFIDENCE = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "NONE",
    }

    def __init__(
        self,
        case_id,
        machine_id,
        source,
        event,
        expected=None,
        observed=None,
        outcome="UNKNOWN",
        confidence="NONE",
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

        self.source = self._require_identifier(
            source,
            "source",
        ).upper()

        self.event = self._require_identifier(
            event,
            "event",
        ).upper()

        self.expected = deepcopy(
            expected
        )

        self.observed = deepcopy(
            observed
        )

        self.outcome = self._normalize_choice(
            outcome,
            self._OUTCOMES,
            "outcome",
        )

        self.confidence = self._normalize_choice(
            confidence,
            self._CONFIDENCE,
            "confidence",
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

    @staticmethod
    def _normalize_choice(
        value,
        allowed,
        field_name,
    ):
        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"{field_name} must be "
                "a supported string value."
            )

        normalized = value.strip().upper()

        if normalized not in allowed:
            raise ValueError(
                f"Unsupported {field_name}: "
                f"{value!r}."
            )

        return normalized

    def to_dict(self):
        return {
            "feedback_id": self.feedback_id,
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "source": self.source,
            "event": self.event,
            "expected": deepcopy(
                self.expected
            ),
            "observed": deepcopy(
                self.observed
            ),
            "outcome": self.outcome,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": deepcopy(
                self.metadata
            ),
        }
