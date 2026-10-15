import pytest

from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    ReleaseCandidateState,
)
from packaging.release_candidate_architecture import (
    ReleaseCandidateArchitecture,
    build_release_candidate_architecture,
    release_candidate_architecture_is_consistent,
    release_candidate_architecture_is_ready,
)
from packaging.release_gates import ReleaseGate
from packaging.release_manifest import ReleaseValidationEvidence


def _all_evidence() -> tuple[ReleaseValidationEvidence, ...]:
    return tuple(
        ReleaseValidationEvidence(
            gate=gate,
            passed=True,
            summary=f"{gate.value} validation passed.",
            source=f"tests/{gate.value.lower()}",
        )
        for gate in ReleaseGate
    )


def test_architecture_builds_from_complete_evidence():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert isinstance(architecture, ReleaseCandidateArchitecture)


def test_architecture_uses_canonical_contract():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.contract == RELEASE_CANDIDATE_CONTRACT


def test_architecture_contains_all_required_gates():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.required_gates == tuple(ReleaseGate)


def test_complete_architecture_is_ready():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.readiness.state is ReleaseCandidateState.READY
    assert release_candidate_architecture_is_ready(architecture)


def test_complete_architecture_is_consistent():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert release_candidate_architecture_is_consistent(architecture)


def test_manifest_and_readiness_match():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.manifest.state == architecture.readiness.state
    assert architecture.manifest.passed_gates == architecture.readiness.passed_gates
    assert architecture.manifest.failed_gates == architecture.readiness.failed_gates
    assert architecture.manifest.blockers == architecture.readiness.blockers


def test_manifest_identity_matches_contract():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.manifest.identity == architecture.contract.identity


def test_missing_gate_blocks_architecture():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.SECURITY
    )

    architecture = build_release_candidate_architecture(evidence)

    assert architecture.readiness.state is ReleaseCandidateState.BLOCKED
    assert not release_candidate_architecture_is_ready(architecture)


def test_failed_gate_blocks_architecture():
    evidence = tuple(
        ReleaseValidationEvidence(
            gate=item.gate,
            passed=False if item.gate is ReleaseGate.SECURITY else True,
            summary=(
                "Security validation failed."
                if item.gate is ReleaseGate.SECURITY
                else item.summary
            ),
            source=item.source,
        )
        for item in _all_evidence()
    )

    architecture = build_release_candidate_architecture(evidence)

    assert architecture.readiness.state is ReleaseCandidateState.BLOCKED
    assert not release_candidate_architecture_is_ready(architecture)


def test_architecture_is_frozen():
    architecture = build_release_candidate_architecture(_all_evidence())

    with pytest.raises(Exception):
        architecture.readiness = architecture.readiness


def test_architecture_rejects_non_tuple_evidence():
    with pytest.raises(TypeError):
        build_release_candidate_architecture([])


def test_architecture_rejects_invalid_contract():
    with pytest.raises(TypeError):
        build_release_candidate_architecture(
            _all_evidence(),
            contract="invalid",
        )


def test_consistency_rejects_invalid_type():
    assert release_candidate_architecture_is_consistent(None) is False


def test_ready_rejects_invalid_type():
    assert release_candidate_architecture_is_ready(None) is False


def test_blocked_architecture_can_still_be_consistent():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.PACKAGING
    )

    architecture = build_release_candidate_architecture(evidence)

    assert architecture.readiness.state is ReleaseCandidateState.BLOCKED
    assert release_candidate_architecture_is_consistent(architecture)


def test_architecture_preserves_evidence():
    evidence = _all_evidence()
    architecture = build_release_candidate_architecture(evidence)

    assert architecture.manifest.evidence == evidence


def test_v09_beta_identity_is_preserved():
    architecture = build_release_candidate_architecture(_all_evidence())

    assert architecture.contract.identity.version == "1.0.0"
    assert architecture.contract.identity.release_channel == "production"
