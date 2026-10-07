"""Release candidate gates and readiness evaluation."""

from dataclasses import dataclass
from enum import Enum

from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    ReleaseCandidateContract,
    ReleaseCandidateState,
)


class ReleaseGate(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    TESTS = "TESTS"
    PACKAGING = "PACKAGING"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    ENVIRONMENT = "ENVIRONMENT"
    DOCUMENTATION = "DOCUMENTATION"


@dataclass(frozen=True)
class ReleaseGateResult:
    gate: ReleaseGate
    passed: bool
    evidence: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.gate, ReleaseGate):
            raise TypeError("gate must be a ReleaseGate.")

        if not isinstance(self.passed, bool):
            raise TypeError("passed must be a boolean.")

        if not isinstance(self.evidence, str):
            raise TypeError("evidence must be a string.")


@dataclass(frozen=True)
class ReleaseReadiness:
    state: ReleaseCandidateState
    passed_gates: tuple[ReleaseGate, ...]
    failed_gates: tuple[ReleaseGate, ...]
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.state, ReleaseCandidateState):
            raise TypeError("state must be a ReleaseCandidateState.")

        for collection in (
            self.passed_gates,
            self.failed_gates,
            self.blockers,
        ):
            if not isinstance(collection, tuple):
                raise TypeError("readiness collections must be tuples.")


REQUIRED_RELEASE_GATES = tuple(ReleaseGate)


def evaluate_release_readiness(
    gate_results: tuple[ReleaseGateResult, ...],
    contract: ReleaseCandidateContract = RELEASE_CANDIDATE_CONTRACT,
) -> ReleaseReadiness:
    if not isinstance(gate_results, tuple):
        raise TypeError("gate_results must be a tuple.")

    if not isinstance(contract, ReleaseCandidateContract):
        raise TypeError("contract must be a ReleaseCandidateContract.")

    results_by_gate = {result.gate: result for result in gate_results}

    passed = tuple(
        gate
        for gate in REQUIRED_RELEASE_GATES
        if gate in results_by_gate and results_by_gate[gate].passed
    )

    failed = tuple(
        gate
        for gate in REQUIRED_RELEASE_GATES
        if gate not in results_by_gate or not results_by_gate[gate].passed
    )

    blockers = tuple(
        (
            f"{gate.value}: "
            + (
                results_by_gate[gate].evidence
                if gate in results_by_gate and results_by_gate[gate].evidence
                else "required release gate has not passed"
            )
        )
        for gate in failed
    )

    if failed:
        state = ReleaseCandidateState.BLOCKED
    elif not contract.required_components:
        state = ReleaseCandidateState.BLOCKED
        blockers = ("RC contract has no required components.",)
    else:
        state = ReleaseCandidateState.READY

    return ReleaseReadiness(
        state=state,
        passed_gates=passed,
        failed_gates=failed,
        blockers=blockers,
    )


def release_readiness_is_ready(readiness: ReleaseReadiness) -> bool:
    if not isinstance(readiness, ReleaseReadiness):
        return False

    return (
        readiness.state is ReleaseCandidateState.READY
        and not readiness.failed_gates
        and not readiness.blockers
        and set(readiness.passed_gates) == set(REQUIRED_RELEASE_GATES)
    )
