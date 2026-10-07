from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4


class RootCauseFeedback:
    """
    Passive feedback record for a root-cause candidate
    and its later observed effect.

    Feedback does not prove causation and does not
    modify diagnostic intelligence.
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
        root_cause_id,
        root_cause,
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

        self.root_cause_id = self._require_identifier(
            root_cause_id,
            "root_cause_id",
        ).upper()

        if root_cause is None:
            raise ValueError("root_cause is required.")

        if expected_effect is None:
            raise ValueError(
                "expected_effect is required."
            )

        self.root_cause = deepcopy(root_cause)
        self.expected_effect = deepcopy(expected_effect)
        self.observed_effect = deepcopy(observed_effect)

        self.outcome = self._normalize_outcome(outcome)

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
            "root_cause_id": self.root_cause_id,
            "root_cause": deepcopy(self.root_cause),
            "expected_effect": deepcopy(
                self.expected_effect
            ),
            "observed_effect": deepcopy(
                self.observed_effect
            ),
            "outcome": self.outcome,
            "timestamp": self.timestamp,
            "metadata": deepcopy(self.metadata),
        }
