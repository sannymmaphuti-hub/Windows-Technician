"""Final release-readiness integration."""

from dataclasses import dataclass

from packaging.release_candidate import ReleaseCandidateState
from packaging.release_manifest import ReleaseValidationEvidence
from packaging.release_validation import (
    ReleaseValidationResult,
    validate_release_candidate,
    release_validation_passed,
)


@dataclass(frozen=True)
class FinalReleaseReadiness:
    validation: ReleaseValidationResult
    ready_for_next_phase: bool

    def __post_init__(self) -> None:
        if not isinstance(self.validation, ReleaseValidationResult):
            raise TypeError(
                "validation must be a ReleaseValidationResult."
            )

        if not isinstance(self.ready_for_next_phase, bool):
            raise TypeError(
                "ready_for_next_phase must be a boolean."
            )


def evaluate_final_release_readiness(
    evidence: tuple[ReleaseValidationEvidence, ...],
) -> FinalReleaseReadiness:
    if not isinstance(evidence, tuple):
        raise TypeError("evidence must be a tuple.")

    validation = validate_release_candidate(evidence)

    return FinalReleaseReadiness(
        validation=validation,
        ready_for_next_phase=release_validation_passed(validation),
    )


def final_release_readiness_passed(
    result: FinalReleaseReadiness,
) -> bool:
    if not isinstance(result, FinalReleaseReadiness):
        return False

    return (
        result.ready_for_next_phase
        and result.validation.state is ReleaseCandidateState.READY
        and release_validation_passed(result.validation)
    )


def final_release_readiness_blocked(
    result: FinalReleaseReadiness,
) -> bool:
    if not isinstance(result, FinalReleaseReadiness):
        return False

    return (
        result.validation.state is ReleaseCandidateState.BLOCKED
        and not result.ready_for_next_phase
    )
