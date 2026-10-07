"""Canonical beta/production release candidate architecture."""

from dataclasses import dataclass

from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    ReleaseCandidateContract,
    ReleaseCandidateState,
)
from packaging.release_gates import (
    REQUIRED_RELEASE_GATES,
    ReleaseGate,
    ReleaseGateResult,
    ReleaseReadiness,
    evaluate_release_readiness,
)
from packaging.release_manifest import (
    ReleaseManifest,
    ReleaseValidationEvidence,
    build_release_manifest,
)


@dataclass(frozen=True)
class ReleaseCandidateArchitecture:
    contract: ReleaseCandidateContract
    required_gates: tuple[ReleaseGate, ...]
    readiness: ReleaseReadiness
    manifest: ReleaseManifest

    def __post_init__(self) -> None:
        if not isinstance(self.contract, ReleaseCandidateContract):
            raise TypeError("contract must be a ReleaseCandidateContract.")

        if not isinstance(self.required_gates, tuple):
            raise TypeError("required_gates must be a tuple.")

        if any(
            not isinstance(gate, ReleaseGate)
            for gate in self.required_gates
        ):
            raise TypeError("required_gates must contain ReleaseGate values.")

        if not isinstance(self.readiness, ReleaseReadiness):
            raise TypeError("readiness must be a ReleaseReadiness.")

        if not isinstance(self.manifest, ReleaseManifest):
            raise TypeError("manifest must be a ReleaseManifest.")


def build_release_candidate_architecture(
    evidence: tuple[ReleaseValidationEvidence, ...],
    contract: ReleaseCandidateContract = RELEASE_CANDIDATE_CONTRACT,
) -> ReleaseCandidateArchitecture:
    if not isinstance(evidence, tuple):
        raise TypeError("evidence must be a tuple.")

    readiness = evaluate_release_readiness(
        tuple(
            ReleaseGateResult(
                gate=item.gate,
                passed=item.passed,
                evidence=item.summary,
            )
            for item in evidence
        ),
        contract,
    )

    manifest = build_release_manifest(
        evidence,
        contract,
    )

    return ReleaseCandidateArchitecture(
        contract=contract,
        required_gates=REQUIRED_RELEASE_GATES,
        readiness=readiness,
        manifest=manifest,
    )


def release_candidate_architecture_is_consistent(
    architecture: ReleaseCandidateArchitecture,
) -> bool:
    if not isinstance(architecture, ReleaseCandidateArchitecture):
        return False

    if architecture.required_gates != REQUIRED_RELEASE_GATES:
        return False

    if architecture.manifest.identity != architecture.contract.identity:
        return False

    if architecture.readiness.state != architecture.manifest.state:
        return False

    if architecture.readiness.passed_gates != architecture.manifest.passed_gates:
        return False

    if architecture.readiness.failed_gates != architecture.manifest.failed_gates:
        return False

    if architecture.readiness.blockers != architecture.manifest.blockers:
        return False

    return True


def release_candidate_architecture_is_ready(
    architecture: ReleaseCandidateArchitecture,
) -> bool:
    if not release_candidate_architecture_is_consistent(architecture):
        return False

    return architecture.readiness.state is ReleaseCandidateState.READY
