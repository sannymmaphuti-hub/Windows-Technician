"""Release candidate validation pipeline."""

from dataclasses import dataclass

from packaging.release_candidate import (
    ReleaseCandidateState,
)
from packaging.release_candidate_architecture import (
    ReleaseCandidateArchitecture,
    build_release_candidate_architecture,
    release_candidate_architecture_is_consistent,
    release_candidate_architecture_is_ready,
)
from packaging.release_manifest import ReleaseValidationEvidence


@dataclass(frozen=True)
class ReleaseValidationResult:
    state: ReleaseCandidateState
    architecture: ReleaseCandidateArchitecture
    validated: bool

    def __post_init__(self) -> None:
        if not isinstance(self.state, ReleaseCandidateState):
            raise TypeError("state must be a ReleaseCandidateState.")

        if not isinstance(self.architecture, ReleaseCandidateArchitecture):
            raise TypeError(
                "architecture must be a ReleaseCandidateArchitecture."
            )

        if not isinstance(self.validated, bool):
            raise TypeError("validated must be a boolean.")


def validate_release_candidate(
    evidence: tuple[ReleaseValidationEvidence, ...],
) -> ReleaseValidationResult:
    if not isinstance(evidence, tuple):
        raise TypeError("evidence must be a tuple.")

    architecture = build_release_candidate_architecture(evidence)

    consistent = release_candidate_architecture_is_consistent(
        architecture
    )

    ready = release_candidate_architecture_is_ready(
        architecture
    )

    validated = consistent and (
        ready
        or architecture.readiness.state is ReleaseCandidateState.BLOCKED
    )

    return ReleaseValidationResult(
        state=architecture.readiness.state,
        architecture=architecture,
        validated=validated,
    )


def release_validation_passed(
    result: ReleaseValidationResult,
) -> bool:
    if not isinstance(result, ReleaseValidationResult):
        return False

    return (
        result.validated
        and result.state is ReleaseCandidateState.READY
        and release_candidate_architecture_is_ready(result.architecture)
    )


def release_validation_blocked(
    result: ReleaseValidationResult,
) -> bool:
    if not isinstance(result, ReleaseValidationResult):
        return False

    return (
        result.validated
        and result.state is ReleaseCandidateState.BLOCKED
    )
