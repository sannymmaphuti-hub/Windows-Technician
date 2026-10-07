# ==========================================
# Windows Technician v0.9
# PREDICTION VS OUTCOME COMPARISON
# ==========================================

from copy import deepcopy

from engine.intelligence_feedback import (
    IntelligenceFeedback,
)


class OutcomeComparison:
    """
    Compares expected and observed intelligence
    feedback values.

    Phase 7.3 determines whether an intelligence
    prediction was:

        CONFIRMED
        PARTIAL
        REFUTED
        UNKNOWN

    This component is analytical only.

    It must NOT:
        - modify feedback history
        - modify the feedback record
        - change confidence
        - generate recommendations
        - authorize remediation
        - execute remediation
        - create learning signals

    Learning begins in later Phase 7 layers.
    """

    def compare(self, feedback):
        if not isinstance(
            feedback,
            IntelligenceFeedback,
        ):
            raise ValueError(
                "Outcome comparison requires "
                "an IntelligenceFeedback record."
            )

        expected = feedback.expected
        observed = feedback.observed

        if expected is None or observed is None:
            outcome = "UNKNOWN"
            matched_fields = 0
            compared_fields = 0

        elif isinstance(expected, dict) and isinstance(
            observed,
            dict,
        ):
            outcome, matched_fields, compared_fields = (
                self._compare_dicts(
                    expected,
                    observed,
                )
            )

        else:
            outcome = (
                "CONFIRMED"
                if expected == observed
                else "REFUTED"
            )

            matched_fields = (
                1
                if expected == observed
                else 0
            )

            compared_fields = 1

        return {
            "feedback_id": feedback.feedback_id,
            "case_id": feedback.case_id,
            "machine_id": feedback.machine_id,
            "expected": deepcopy(expected),
            "observed": deepcopy(observed),
            "outcome": outcome,
            "confidence": feedback.confidence,
            "matched_fields": matched_fields,
            "compared_fields": compared_fields,
        }

    @classmethod
    def _compare_dicts(
        cls,
        expected,
        observed,
    ):
        if not expected and not observed:
            return (
                "UNKNOWN",
                0,
                0,
            )

        compared_fields = len(expected)
        matched_fields = 0

        for key, expected_value in expected.items():
            if key not in observed:
                continue

            if cls._values_equal(
                expected_value,
                observed[key],
            ):
                matched_fields += 1

        if compared_fields == 0:
            return (
                "UNKNOWN",
                0,
                0,
            )

        if matched_fields == compared_fields:
            return (
                "CONFIRMED",
                matched_fields,
                compared_fields,
            )

        if matched_fields == 0:
            return (
                "REFUTED",
                0,
                compared_fields,
            )

        return (
            "PARTIAL",
            matched_fields,
            compared_fields,
        )

    @staticmethod
    def _values_equal(
        expected,
        observed,
    ):
        return expected == observed

