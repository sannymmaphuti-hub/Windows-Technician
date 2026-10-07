"""Release candidate validation evidence and manifest."""

from dataclasses import dataclass

from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    ReleaseCandidateContract,
    ReleaseCandidateIdentity,
    ReleaseCandidateState,
)
from packaging.release_gates import (
    ReleaseGate,
    ReleaseGateResult,
    ReleaseReadiness,
    evaluate_release_readiness,
)


@dataclass(frozen=True)
class ReleaseValidationEvidence:
    gate: ReleaseGate
    passed: bool
    summary: str
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.gate, ReleaseGate):
            raise TypeError("gate must be a ReleaseGate.")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a boolean.")

        if not isinstance(self.summary, str) or not self.summary.strip():
            raise ValueError("summary must be a non-empty string.")

        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be a non-empty string.")


@dataclass(frozen=True)
class ReleaseManifest:
    identity: ReleaseCandidateIdentity
    state: ReleaseCandidateState
    evidence: tuple[ReleaseValidationEvidence, ...]
    passed_gates: tuple[ReleaseGate, ...]
    failed_gates: tuple[ReleaseGate, ...]
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ReleaseCandidateIdentity):
            raise TypeError("identity must be a ReleaseCandidateIdentity.")

        if not isinstance(self.state, ReleaseCandidateState):
            raise TypeError("state must be a ReleaseCandidateState.")

        for collection in (
            self.evidence,
            self.passed_gates,
            self.failed_gates,
            self.blockers,
        ):
            if not isinstance(collection, tuple):
                raise TypeError("manifest collections must be tuples.")


def validation_evidence_to_gate_result(
    evidence: ReleaseValidationEvidence,
) -> ReleaseGateResult:
    if not isinstance(evidence, ReleaseValidationEvidence):
        raise TypeError("evidence must be ReleaseValidationEvidence.")

    return ReleaseGateResult(
        gate=evidence.gate,
        passed=evidence.passed,
        evidence=evidence.summary,
    )


def build_release_manifest(
    evidence: tuple[ReleaseValidationEvidence, ...],
    contract: ReleaseCandidateContract = RELEASE_CANDIDATE_CONTRACT,
) -> ReleaseManifest:
    if not isinstance(evidence, tuple):
        raise TypeError("evidence must be a tuple.")

    if not isinstance(contract, ReleaseCandidateContract):
        raise TypeError("contract must be a ReleaseCandidateContract.")

    gate_results = tuple(
        validation_evidence_to_gate_result(item)
        for item in evidence
    )

    readiness: ReleaseReadiness = evaluate_release_readiness(
        gate_results,
        contract,
    )

    return ReleaseManifest(
        identity=contract.identity,
        state=readiness.state,
        evidence=evidence,
        passed_gates=readiness.passed_gates,
        failed_gates=readiness.failed_gates,
        blockers=readiness.blockers,
    )


def release_manifest_is_ready(manifest: ReleaseManifest) -> bool:
    if not isinstance(manifest, ReleaseManifest):
        return False

    return (
        manifest.state is ReleaseCandidateState.READY
        and not manifest.failed_gates
        and not manifest.blockers
    )
