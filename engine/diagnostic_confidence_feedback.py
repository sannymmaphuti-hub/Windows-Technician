from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


class DiagnosticConfidenceFeedback:
    """
    Passive feedback record for diagnostic confidence.

    This component records the confidence held at the time
    of diagnosis and any later observed confidence signal.

    It does not automatically change diagnostic confidence
    and does not create learning signals.
    """

    _CONFIDENCE = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "NONE",
    }

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
        diagnostic_id,
        confidence,
        expected_confidence="NONE",
        observed_confidence="NONE",
        outcome="UNKNOWN",
        evidence=None,
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

        self.diagnostic_id = self._require_identifier(
            diagnostic_id,
            "diagnostic_id",
        ).upper()

        self.confidence = self._normalize_confidence(
            confidence,
            "confidence",
        )

        self.expected_confidence = (
            self._normalize_confidence(
                expected_confidence,
                "expected_confidence",
            )
        )

        self.observed_confidence = (
            self._normalize_confidence(
                observed_confidence,
                "observed_confidence",
            )
        )

        self.outcome = self._normalize_outcome(
            outcome
        )

        self.evidence = deepcopy(
            evidence if isinstance(evidence, dict) else {}
        )

        self.metadata = deepcopy(
            metadata if isinstance(metadata, dict) else {}
        )

        self.feedback_id = str(uuid4())

        self.timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    @staticmethod
    def _require_identifier(value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a non-empty string."
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} must be a non-empty string."
            )

        return normalized

    @classmethod
    def _normalize_confidence(cls, value, field_name):
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a supported string value."
            )

        normalized = value.strip().upper()

        if normalized not in cls._CONFIDENCE:
            raise ValueError(
                f"Unsupported {field_name}: {value!r}."
            )

        return normalized

    @classmethod
    def _normalize_outcome(cls, outcome):
        if not isinstance(outcome, str):
            raise ValueError(
                "outcome must be a supported string value."
            )

        normalized = outcome.strip().upper()

        if normalized not in cls._OUTCOMES:
            raise ValueError(
                f"Unsupported outcome: {outcome!r}."
            )

        return normalized

    def to_dict(self):
        return {
            "feedback_id": self.feedback_id,
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "diagnostic_id": self.diagnostic_id,
            "confidence": self.confidence,
            "expected_confidence": self.expected_confidence,
            "observed_confidence": self.observed_confidence,
            "outcome": self.outcome,
            "evidence": deepcopy(self.evidence),
            "metadata": deepcopy(self.metadata),
            "timestamp": self.timestamp,
        }
