import pytest

from packaging.release_candidate import (
    RELEASE_CANDIDATE_REQUIRED_COMPONENTS,
    ReleaseCandidateState,
)
from packaging.release_gates import ReleaseGate
from packaging.release_manifest import ReleaseValidationEvidence
from packaging.release_readiness import (
    FinalReleaseReadiness,
    evaluate_final_release_readiness,
    final_release_readiness_blocked,
    final_release_readiness_passed,
)


def all_evidence():
    return tuple(
        ReleaseValidationEvidence(
            gate=gate,
            passed=True,
            summary=f"{gate.value} passed.",
            source="phase-10-validation",
        )
        for gate in ReleaseGate
    )


def test_final_readiness_passes_with_all_evidence():
    result = evaluate_final_release_readiness(all_evidence())

    assert result.ready_for_next_phase is True
    assert result.validation.state is ReleaseCandidateState.READY
    assert final_release_readiness_passed(result) is True
    assert final_release_readiness_blocked(result) is False


def test_final_readiness_blocks_when_evidence_is_missing():
    evidence = all_evidence()[:-1]

    result = evaluate_final_release_readiness(evidence)

    assert result.validation.state is ReleaseCandidateState.BLOCKED
    assert result.ready_for_next_phase is False
    assert final_release_readiness_passed(result) is False
    assert final_release_readiness_blocked(result) is True


def test_final_readiness_blocks_failed_gate():
    evidence = tuple(
        ReleaseValidationEvidence(
            gate=item.gate,
            passed=False if item.gate is ReleaseGate.SECURITY else item.passed,
            summary=item.summary,
            source=item.source,
        )
        for item in all_evidence()
    )

    result = evaluate_final_release_readiness(evidence)

    assert result.validation.state is ReleaseCandidateState.BLOCKED
    assert result.ready_for_next_phase is False
    assert final_release_readiness_blocked(result) is True


def test_final_readiness_contains_validation():
    result = evaluate_final_release_readiness(all_evidence())

    assert result.validation is not None
    assert result.validation.architecture is not None


def test_final_readiness_is_frozen():
    result = evaluate_final_release_readiness(all_evidence())

    with pytest.raises(AttributeError):
        result.ready_for_next_phase = False


def test_final_readiness_rejects_invalid_evidence_container():
    with pytest.raises(TypeError):
        evaluate_final_release_readiness([])


def test_final_readiness_pass_helper_rejects_invalid_value():
    assert final_release_readiness_passed(None) is False


def test_final_readiness_block_helper_rejects_invalid_value():
    assert final_release_readiness_blocked(None) is False


def test_final_readiness_preserves_required_components():
    result = evaluate_final_release_readiness(all_evidence())

    assert result.validation.architecture.contract.required_components == (
        RELEASE_CANDIDATE_REQUIRED_COMPONENTS
    )


def test_ready_candidate_is_not_blocked():
    result = evaluate_final_release_readiness(all_evidence())

    assert result.validation.state is ReleaseCandidateState.READY
    assert final_release_readiness_blocked(result) is False
