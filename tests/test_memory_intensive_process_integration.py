from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_engine import RootCauseEngine
from engine.memory_intensive_process_rule import (
    MemoryIntensiveProcessRule,
)


def create_memory_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_cpu_finding():

    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )


def create_engine():

    engine = RootCauseEngine()

    engine.register_rule(
        MemoryIntensiveProcessRule()
    )

    return engine


def test_memory_pressure_generates_memory_intensive_process_candidate():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert len(candidates) == 1

    candidate = candidates[0]

    assert isinstance(
        candidate,
        RootCauseCandidate,
    )

    assert (
        candidate.cause_type
        == "MEMORY_INTENSIVE_PROCESS"
    )

    assert candidate.category == "MEMORY"


def test_cpu_pressure_does_not_generate_memory_process_candidate():

    engine = create_engine()

    candidates = engine.detect(
        [create_cpu_finding()]
    )

    assert candidates == []


def test_memory_candidate_explanation_preserves_uncertainty():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    explanation = candidates[0].explanation

    assert "may" in explanation
    assert "possible" in explanation


def test_memory_candidate_is_not_selected_as_primary_cause():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    candidate = candidates[0]

    assert not hasattr(
        candidate,
        "is_primary",
    )

    assert not hasattr(
        candidate,
        "selected",
    )


def test_root_cause_engine_uses_real_memory_rule():

    engine = create_engine()

    candidates = engine.detect(
        [create_memory_finding()]
    )

    assert [
        candidate.cause_type
        for candidate in candidates
    ] == [
        "MEMORY_INTENSIVE_PROCESS"
    ]