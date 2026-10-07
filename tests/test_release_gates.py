import pytest

from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    ReleaseCandidateState,
)
from packaging.release_gates import (
    REQUIRED_RELEASE_GATES,
    ReleaseGate,
    ReleaseGateResult,
    ReleaseReadiness,
    evaluate_release_readiness,
    release_readiness_is_ready,
)


def _all_passed() -> tuple[ReleaseGateResult, ...]:
    return tuple(
        ReleaseGateResult(
            gate=gate,
            passed=True,
            evidence=f"{gate.value} gate passed.",
        )
        for gate in REQUIRED_RELEASE_GATES
    )


def test_all_required_gates_are_defined():
    assert REQUIRED_RELEASE_GATES == (
        ReleaseGate.ARCHITECTURE,
        ReleaseGate.TESTS,
        ReleaseGate.PACKAGING,
        ReleaseGate.SECURITY,
        ReleaseGate.PERFORMANCE,
        ReleaseGate.ENVIRONMENT,
        ReleaseGate.DOCUMENTATION,
    )


def test_gate_result_is_frozen():
    result = ReleaseGateResult(
        gate=ReleaseGate.TESTS,
        passed=True,
    )

    with pytest.raises(Exception):
        result.passed = False


def test_all_gates_passing_produces_ready():
    readiness = evaluate_release_readiness(_all_passed())

    assert readiness.state is ReleaseCandidateState.READY
    assert readiness.failed_gates == ()
    assert readiness.blockers == ()
    assert release_readiness_is_ready(readiness)


def test_missing_gate_blocks_release():
    results = tuple(
        result
        for result in _all_passed()
        if result.gate is not ReleaseGate.SECURITY
    )

    readiness = evaluate_release_readiness(results)

    assert readiness.state is ReleaseCandidateState.BLOCKED
    assert ReleaseGate.SECURITY in readiness.failed_gates
    assert readiness.blockers


def test_failed_gate_blocks_release():
    results = _all_passed()
    results = tuple(
        ReleaseGateResult(
            gate=result.gate,
            passed=False if result.gate is ReleaseGate.SECURITY else result.passed,
            evidence=(
                "Security validation failed."
                if result.gate is ReleaseGate.SECURITY
                else result.evidence
            ),
        )
        for result in results
    )

    readiness = evaluate_release_readiness(results)

    assert readiness.state is ReleaseCandidateState.BLOCKED
    assert ReleaseGate.SECURITY in readiness.failed_gates
    assert any("Security validation failed." in blocker for blocker in readiness.blockers)


def test_passed_gates_are_recorded():
    readiness = evaluate_release_readiness(_all_passed())

    assert set(readiness.passed_gates) == set(REQUIRED_RELEASE_GATES)


def test_failed_gates_are_recorded():
    results = tuple(
        result
        for result in _all_passed()
        if result.gate is not ReleaseGate.TESTS
    )

    readiness = evaluate_release_readiness(results)

    assert ReleaseGate.TESTS in readiness.failed_gates


def test_readiness_requires_correct_type():
    assert release_readiness_is_ready(None) is False


def test_gate_result_requires_valid_gate():
    with pytest.raises(TypeError):
        ReleaseGateResult(
            gate="TESTS",
            passed=True,
        )


def test_gate_result_requires_boolean_passed_value():
    with pytest.raises(TypeError):
        ReleaseGateResult(
            gate=ReleaseGate.TESTS,
            passed="yes",
        )


def test_gate_result_requires_string_evidence():
    with pytest.raises(TypeError):
        ReleaseGateResult(
            gate=ReleaseGate.TESTS,
            passed=True,
            evidence=None,
        )


def test_evaluation_requires_tuple():
    with pytest.raises(TypeError):
        evaluate_release_readiness([])


def test_evaluation_requires_contract_type():
    with pytest.raises(TypeError):
        evaluate_release_readiness(
            _all_passed(),
            contract="invalid",
        )


def test_empty_gate_results_block_release():
    readiness = evaluate_release_readiness(())

    assert readiness.state is ReleaseCandidateState.BLOCKED
    assert len(readiness.failed_gates) == len(REQUIRED_RELEASE_GATES)


def test_ready_state_has_no_blockers():
    readiness = evaluate_release_readiness(_all_passed())

    assert readiness.blockers == ()


def test_blocked_state_is_not_ready():
    results = tuple(
        result
        for result in _all_passed()
        if result.gate is not ReleaseGate.TESTS
    )

    readiness = evaluate_release_readiness(results)

    assert not release_readiness_is_ready(readiness)
    assert readiness.state is ReleaseCandidateState.BLOCKED


def test_contract_is_used_by_default():
    readiness = evaluate_release_readiness(_all_passed())

    assert readiness is not None
    assert RELEASE_CANDIDATE_CONTRACT.required_components


def test_readiness_is_immutable():
    readiness = evaluate_release_readiness(_all_passed())

    with pytest.raises(Exception):
        readiness.state = ReleaseCandidateState.BLOCKED
