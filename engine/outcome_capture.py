# ==========================================
# Windows Technician v0.9
# OUTCOME CAPTURE
# ==========================================

from copy import deepcopy

from engine.intelligence_feedback import (
    IntelligenceFeedback,
)


_UNSET = object()


class OutcomeCapture:
    """
    Captures a later observed outcome for an
    intelligence feedback record.

    Phase 7.2 is intentionally passive.

    This component:
        - preserves the original intelligence event
        - records the later observed value
        - creates a new feedback record
        - links the new record to the original
        - preserves uncertainty when no outcome is known

    This component must NOT:
        - compare expected and observed values
        - determine whether a prediction was correct
        - modify the original feedback record
        - modify diagnostic history
        - modify root-cause candidates
        - modify confidence
        - generate recommendations
        - authorize remediation
        - execute remediation

    Prediction/outcome comparison belongs to Phase 7.3.
    """

    def capture(
        self,
        feedback,
        observed=_UNSET,
        outcome="UNKNOWN",
        metadata=None,
    ):
        if not isinstance(
            feedback,
            IntelligenceFeedback,
        ):
            raise ValueError(
                "Outcome capture requires "
                "an IntelligenceFeedback record."
            )

        if observed is _UNSET:
            raise ValueError(
                "Outcome capture requires "
                "an observed value."
            )

        if observed is None:
            captured_observed = None
        else:
            captured_observed = deepcopy(
                observed
            )

        captured_metadata = deepcopy(
            feedback.metadata
        )

        if not isinstance(
            captured_metadata,
            dict,
        ):
            captured_metadata = {}

        captured_metadata[
            "source_feedback_id"
        ] = feedback.feedback_id

        if metadata is not None:
            if not isinstance(
                metadata,
                dict,
            ):
                raise ValueError(
                    "Outcome metadata must "
                    "be a dictionary."
                )

            captured_metadata.update(
                deepcopy(metadata)
            )

        return IntelligenceFeedback(
            case_id=feedback.case_id,
            machine_id=feedback.machine_id,
            source="OUTCOME_CAPTURE",
            event="OUTCOME",
            expected=deepcopy(
                feedback.expected
            ),
            observed=captured_observed,
            outcome=outcome,
            confidence=feedback.confidence,
            metadata=captured_metadata,
        )

