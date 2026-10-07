import pytest

from packaging.release_candidate import (
    ReleaseCandidateState,
)
from packaging.release_gates import ReleaseGate
from packaging.release_manifest import (
    ReleaseManifest,
    ReleaseValidationEvidence,
    build_release_manifest,
    release_manifest_is_ready,
    validation_evidence_to_gate_result,
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


def test_validation_evidence_requires_valid_gate():
    with pytest.raises(TypeError):
        ReleaseValidationEvidence(
            gate="TESTS",
            passed=True,
            summary="passed",
            source="tests",
        )


def test_validation_evidence_requires_boolean_result():
    with pytest.raises(TypeError):
        ReleaseValidationEvidence(
            gate=ReleaseGate.TESTS,
            passed="yes",
            summary="passed",
            source="tests",
        )


def test_validation_evidence_requires_summary():
    with pytest.raises(ValueError):
        ReleaseValidationEvidence(
            gate=ReleaseGate.TESTS,
            passed=True,
            summary="",
            source="tests",
        )


def test_validation_evidence_requires_source():
    with pytest.raises(ValueError):
        ReleaseValidationEvidence(
            gate=ReleaseGate.TESTS,
            passed=True,
            summary="passed",
            source="",
        )


def test_evidence_converts_to_gate_result():
    evidence = ReleaseValidationEvidence(
        gate=ReleaseGate.TESTS,
        passed=True,
        summary="45 release-gate tests passed.",
        source="tests/test_release_gates.py",
    )

    result = validation_evidence_to_gate_result(evidence)

    assert result.gate is ReleaseGate.TESTS
    assert result.passed is True
    assert result.evidence == "45 release-gate tests passed."


def test_complete_evidence_produces_ready_manifest():
    manifest = build_release_manifest(_all_evidence())

    assert manifest.state is ReleaseCandidateState.READY
    assert manifest.failed_gates == ()
    assert manifest.blockers == ()
    assert release_manifest_is_ready(manifest)


def test_missing_evidence_blocks_manifest():
    evidence = tuple(
        item
        for item in _all_evidence()
        if item.gate is not ReleaseGate.SECURITY
    )

    manifest = build_release_manifest(evidence)

    assert manifest.state is ReleaseCandidateState.BLOCKED
    assert ReleaseGate.SECURITY in manifest.failed_gates
    assert manifest.blockers
    assert not release_manifest_is_ready(manifest)


def test_failed_evidence_blocks_manifest():
    evidence = tuple(
        ReleaseValidationEvidence(
            gate=item.gate,
            passed=False if item.gate is ReleaseGate.SECURITY else item.passed,
            summary=(
                "Security validation failed."
                if item.gate is ReleaseGate.SECURITY
                else item.summary
            ),
            source=item.source,
        )
        for item in _all_evidence()
    )

    manifest = build_release_manifest(evidence)

    assert manifest.state is ReleaseCandidateState.BLOCKED
    assert ReleaseGate.SECURITY in manifest.failed_gates
    assert not release_manifest_is_ready(manifest)


def test_manifest_preserves_all_evidence():
    evidence = _all_evidence()
    manifest = build_release_manifest(evidence)

    assert manifest.evidence == evidence
    assert len(manifest.evidence) == len(tuple(ReleaseGate))


def test_manifest_contains_identity():
    manifest = build_release_manifest(_all_evidence())

    assert manifest.identity.version == "0.9.0"
    assert manifest.identity.release_channel == "beta"


def test_manifest_is_frozen():
    manifest = build_release_manifest(_all_evidence())

    with pytest.raises(Exception):
        manifest.state = ReleaseCandidateState.BLOCKED


def test_manifest_requires_tuple_evidence():
    with pytest.raises(TypeError):
        ReleaseManifest(
            identity=build_release_manifest(_all_evidence()).identity,
            state=ReleaseCandidateState.READY,
            evidence=[],
            passed_gates=(),
            failed_gates=(),
            blockers=(),
        )


def test_manifest_readiness_rejects_invalid_type():
    assert release_manifest_is_ready(None) is False


def test_evidence_conversion_rejects_invalid_type():
    with pytest.raises(TypeError):
        validation_evidence_to_gate_result("invalid")


def test_manifest_build_requires_tuple():
    with pytest.raises(TypeError):
        build_release_manifest([])


def test_manifest_build_requires_valid_contract():
    with pytest.raises(TypeError):
        build_release_manifest(_all_evidence(), contract="invalid")


def test_manifest_records_passed_gates():
    manifest = build_release_manifest(_all_evidence())

    assert set(manifest.passed_gates) == set(ReleaseGate)


def test_manifest_has_no_blockers_when_ready():
    manifest = build_release_manifest(_all_evidence())

    assert manifest.blockers == ()
