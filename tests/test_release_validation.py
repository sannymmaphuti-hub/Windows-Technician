import pytest

from packaging.release_candidate import ReleaseCandidateState
from packaging.release_gates import ReleaseGate
from packaging.release_manifest import ReleaseValidationEvidence
from packaging.release_validation import (
    ReleaseValidationResult,
    release_validation_blocked,
    release_validation_passed,
    validate_release_candidate,
)


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


def test_complete_validation_produces_ready_result():
    result = validate_release_candidate(_all_evidence())

    assert result.state is ReleaseCandidateState.READY
    assert result.validated is True
    assert release_validation_passed(result)
    assert not release_validation_blocked(result)


def test_missing_evidence_produces_validated_blocked_result():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.SECURITY
    )

    result = validate_release_candidate(evidence)

    assert result.state is ReleaseCandidateState.BLOCKED
    assert result.validated is True
    assert release_validation_blocked(result)
    assert not release_validation_passed(result)


def test_failed_gate_produces_validated_blocked_result():
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

    result = validate_release_candidate(evidence)

    assert result.state is ReleaseCandidateState.BLOCKED
    assert result.validated is True
    assert release_validation_blocked(result)


def test_validation_contains_canonical_architecture():
    result = validate_release_candidate(_all_evidence())

    assert result.architecture.manifest.identity == (
        result.architecture.contract.identity
    )


def test_validation_rejects_non_tuple_evidence():
    with pytest.raises(TypeError):
        validate_release_candidate([])


def test_validation_result_is_frozen():
    result = validate_release_candidate(_all_evidence())

    with pytest.raises(Exception):
        result.validated = False


def test_validation_result_requires_state_type():
    with pytest.raises(TypeError):
        ReleaseValidationResult(
            state="READY",
            architecture=validate_release_candidate(_all_evidence()).architecture,
            validated=True,
        )


def test_validation_result_requires_architecture_type():
    with pytest.raises(TypeError):
        ReleaseValidationResult(
            state=ReleaseCandidateState.READY,
            architecture="invalid",
            validated=True,
        )


def test_validation_result_requires_boolean():
    with pytest.raises(TypeError):
        ReleaseValidationResult(
            state=ReleaseCandidateState.READY,
            architecture=validate_release_candidate(_all_evidence()).architecture,
            validated="yes",
        )


def test_passed_rejects_invalid_result():
    assert release_validation_passed(None) is False


def test_blocked_rejects_invalid_result():
    assert release_validation_blocked(None) is False


def test_blocked_result_is_not_release_pass():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.TESTS
    )

    result = validate_release_candidate(evidence)

    assert release_validation_blocked(result)
    assert not release_validation_passed(result)


def test_ready_result_is_not_blocked():
    result = validate_release_candidate(_all_evidence())

    assert release_validation_passed(result)
    assert not release_validation_blocked(result)


def test_validation_preserves_evidence():
    evidence = _all_evidence()
    result = validate_release_candidate(evidence)

    assert result.architecture.manifest.evidence == evidence


def test_validation_state_matches_architecture():
    result = validate_release_candidate(_all_evidence())

    assert result.state == result.architecture.readiness.state


def test_blocked_validation_preserves_blockers():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.PACKAGING
    )

    result = validate_release_candidate(evidence)

    assert result.architecture.readiness.blockers
    assert result.architecture.manifest.blockers == (
        result.architecture.readiness.blockers
    )
