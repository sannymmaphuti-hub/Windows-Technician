from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.memory_intensive_process_evaluation_rule import (
    MemoryIntensiveProcessEvaluationRule,
)
from engine.memory_leak_evaluation_rule import (
    MemoryLeakEvaluationRule,
)


def create_memory_pressure_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def create_process_memory_finding():

    return Finding(
        finding_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        severity="HIGH",
        description=(
            "A specific process is consuming unusually "
            "large amounts of memory."
        ),
        supporting_signals=[],
    )


def create_memory_growth_finding():

    return Finding(
        finding_type="MEMORY_GROWTH_OVER_TIME",
        category="MEMORY",
        severity="HIGH",
        description=(
            "A process has shown sustained memory growth "
            "over time."
        ),
        supporting_signals=[],
    )


def create_process_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the observed memory pressure."
        ),
    )


def create_leak_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing to the "
            "observed memory pressure."
        ),
    )
def create_pipeline():

    evaluation_engine = RootCauseEvaluationEngine()

    evaluation_engine.register_rule(
        MemoryIntensiveProcessEvaluationRule()
    )

    evaluation_engine.register_rule(
        MemoryLeakEvaluationRule()
    )

    return RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

def create_engine():

    engine = RootCauseEvaluationEngine()

    engine.register_rule(
        MemoryIntensiveProcessEvaluationRule()
    )

    engine.register_rule(
        MemoryLeakEvaluationRule()
    )

    return engine


def test_evaluation_pipeline_returns_evaluations():

    engine = create_engine()

    evaluations = engine.evaluate(
        create_process_candidate(),
        [create_memory_pressure_finding()],
    )

    assert isinstance(
        evaluations,
        list,
    )

    assert all(
        isinstance(
            evaluation,
            RootCauseEvaluation,
        )
        for evaluation in evaluations
    )


def test_process_candidate_is_evaluated_by_process_rule():

    engine = create_engine()

    candidate = create_process_candidate()

    evaluations = engine.evaluate(
        candidate,
        [
            create_memory_pressure_finding(),
            create_process_memory_finding(),
        ],
    )

    assert len(evaluations) == 1

    assert (
        evaluations[0].candidate
        is candidate
    )

    assert (
        evaluations[0].assessment
        == "SUPPORTED"
    )


def test_leak_candidate_is_evaluated_by_leak_rule():

    engine = create_engine()

    candidate = create_leak_candidate()

    evaluations = engine.evaluate(
        candidate,
        [
            create_memory_pressure_finding(),
            create_memory_growth_finding(),
        ],
    )

    assert len(evaluations) == 1

    assert (
        evaluations[0].candidate
        is candidate
    )

    assert (
        evaluations[0].assessment
        == "SUPPORTED"
    )

def test_pipeline_evaluates_multiple_candidates():

    pipeline = create_pipeline()

    candidates = [
        create_process_candidate(),
        create_leak_candidate(),
    ]

    evaluations = pipeline.evaluate(
        candidates,
        [
            create_memory_pressure_finding(),
            create_process_memory_finding(),
        ],
    )

    assert len(evaluations) == 2

    assert (
        evaluations[0].candidate.cause_type
        == "MEMORY_INTENSIVE_PROCESS"
    )

    assert (
        evaluations[0].assessment
        == "SUPPORTED"
    )

    assert (
        evaluations[1].candidate.cause_type
        == "MEMORY_LEAK"
    )

    assert (
        evaluations[1].assessment
        == "INSUFFICIENT"
    )

def test_process_candidate_without_process_evidence_is_insufficient():

    engine = create_engine()

    candidate = create_process_candidate()

    evaluations = engine.evaluate(
        candidate,
        [create_memory_pressure_finding()],
    )

    assert len(evaluations) == 1

    assert (
        evaluations[0].assessment
        == "INSUFFICIENT"
    )


def test_leak_candidate_without_growth_evidence_is_insufficient():

    engine = create_engine()

    candidate = create_leak_candidate()

    evaluations = engine.evaluate(
        candidate,
        [create_memory_pressure_finding()],
    )

    assert len(evaluations) == 1

    assert (
        evaluations[0].assessment
        == "INSUFFICIENT"
    )


def test_evaluation_pipeline_does_not_select_primary_cause():

    engine = create_engine()

    candidate = create_process_candidate()

    evaluations = engine.evaluate(
        candidate,
        [
            create_memory_pressure_finding(),
            create_process_memory_finding(),
        ],
    )

    evaluation = evaluations[0]

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )


def test_evaluation_preserves_candidate_identity():

    engine = create_engine()

    process_candidate = create_process_candidate()

    evaluations = engine.evaluate(
        process_candidate,
        [
            create_memory_pressure_finding(),
            create_process_memory_finding(),
        ],
    )

    assert (
        evaluations[0].candidate
        is process_candidate
    )


def test_evaluation_preserves_findings():

    engine = create_engine()

    memory_pressure = create_memory_pressure_finding()
    process_memory = create_process_memory_finding()

    evaluations = engine.evaluate(
        create_process_candidate(),
        [
            memory_pressure,
            process_memory,
        ],
    )

    evidence = evaluations[0].supporting_evidence

    assert memory_pressure in evidence
    assert process_memory in evidence


def test_different_candidates_can_be_evaluated_independently():

    engine = create_engine()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    process_evaluations = engine.evaluate(
        create_process_candidate(),
        findings,
    )

    leak_evaluations = engine.evaluate(
        create_leak_candidate(),
        findings,
    )

    assert len(process_evaluations) == 1
    assert len(leak_evaluations) == 1

    assert (
        process_evaluations[0].candidate.cause_type
        == "MEMORY_INTENSIVE_PROCESS"
    )

    assert (
        leak_evaluations[0].candidate.cause_type
        == "MEMORY_LEAK"
    )


def test_supported_evaluations_do_not_become_causal_claims():

    engine = create_engine()

    candidate = create_process_candidate()

    evaluations = engine.evaluate(
        candidate,
        [
            create_memory_pressure_finding(),
            create_process_memory_finding(),
        ],
    )

    explanation = evaluations[0].explanation.lower()

    assert "primary" in explanation
    assert (
        "cause" in explanation
        or "underlying" in explanation
    )

