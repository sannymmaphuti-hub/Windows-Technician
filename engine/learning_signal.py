from copy import deepcopy
from datetime import datetime, timezone
from uuid import UUID, uuid4


class LearningSignal:
    """
    Structured learning signal produced from feedback.

    This is an observational artifact for future intelligence.
    It does not automatically modify diagnosis, confidence,
    recommendations, root causes, or remediation state.
    """

    _SIGNAL_TYPES = {
        "PREDICTION",
        "RECOMMENDATION",
        "ROOT_CAUSE",
        "CONFIDENCE",
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
        signal_type,
        subject_id,
        outcome,
        feedback_id=None,
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

        self.signal_type = self._normalize_choice(
            signal_type,
            self._SIGNAL_TYPES,
            "signal_type",
        )

        self.subject_id = self._require_identifier(
            subject_id,
            "subject_id",
        ).upper()

        self.outcome = self._normalize_choice(
            outcome,
            self._OUTCOMES,
            "outcome",
        )

        if feedback_id is None:
            self.feedback_id = None
        else:
            self.feedback_id = (
                self._normalize_feedback_reference(
                    feedback_id
                )
            )

        self.evidence = deepcopy(
            evidence if isinstance(evidence, dict) else {}
        )

        self.metadata = deepcopy(
            metadata if isinstance(metadata, dict) else {}
        )

        self.signal_id = str(uuid4())

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
    def _normalize_feedback_reference(cls, value):
        normalized = cls._require_identifier(
            value,
            "feedback_id",
        )

        try:
            UUID(normalized)
        except ValueError:
            return normalized.upper()

        # UUID references preserve their original representation
        # so cross-record identity remains exact.
        return normalized

    @classmethod
    def _normalize_choice(
        cls,
        value,
        allowed,
        field_name,
    ):
        if not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a supported string value."
            )

        normalized = value.strip().upper()

        if normalized not in allowed:
            raise ValueError(
                f"Unsupported {field_name}: {value!r}."
            )

        return normalized

    def to_dict(self):
        return {
            "signal_id": self.signal_id,
            "feedback_id": self.feedback_id,
            "case_id": self.case_id,
            "machine_id": self.machine_id,
            "signal_type": self.signal_type,
            "subject_id": self.subject_id,
            "outcome": self.outcome,
            "evidence": deepcopy(self.evidence),
            "metadata": deepcopy(self.metadata),
            "timestamp": self.timestamp,
        }
