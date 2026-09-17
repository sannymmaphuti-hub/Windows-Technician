from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_rule import RootCauseRule
from engine.memory_intensive_process_rule import (
    MemoryIntensiveProcessRule,
)


class MemoryLeakRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "MEMORY_PRESSURE"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="MEMORY_LEAK",
            category="MEMORY",
            explanation=(
                "A memory leak may be contributing to the "
                "observed memory pressure. Further evidence "
                "is required to determine whether this is involved."
            ),
        )


def create_memory_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_engine():

    engine = RootCauseEngine()

    engine.register_rule(
        MemoryIntensiveProcessRule()
    )

    engine.register_rule(
        MemoryLeakRule()
    )

    return engine


def test_memory_pressure_can_produce_multiple_root_cause_candidates():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert len(candidates) == 2


def test_competing_candidates_have_different_cause_types():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    cause_types = {
        candidate.cause_type
        for candidate in candidates
    }

    assert cause_types == {
        "MEMORY_INTENSIVE_PROCESS",
        "MEMORY_LEAK",
    }


def test_all_competing_candidates_are_root_cause_candidates():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert all(
        isinstance(candidate, RootCauseCandidate)
        for candidate in candidates
    )


def test_memory_leak_candidate_preserves_uncertainty():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    memory_leak = next(
        candidate
        for candidate in candidates
        if candidate.cause_type == "MEMORY_LEAK"
    )

    assert "may" in memory_leak.explanation
    assert "further evidence" in memory_leak.explanation.lower()


def test_candidate_generation_does_not_select_primary_cause():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    for candidate in candidates:

        assert not hasattr(
            candidate,
            "is_primary",
        )

        assert not hasattr(
            candidate,
            "selected",
        )


def test_competing_candidates_are_preserved_independently():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert candidates[0] is not candidates[1]

    assert (
        candidates[0].cause_type
        != candidates[1].cause_type
    )