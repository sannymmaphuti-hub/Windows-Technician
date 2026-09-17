from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_reasoning import RootCauseReasoning
from engine.root_cause_engine import RootCauseEngine
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.root_cause_selection import RootCauseSelection
from engine.memory_intensive_process_rule import (
    MemoryIntensiveProcessRule,
)
from engine.memory_leak_rule import MemoryLeakRule
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


def create_reasoning_engine():

    candidate_engine = RootCauseEngine()

    candidate_engine.register_rule(
        MemoryIntensiveProcessRule()
    )

    candidate_engine.register_rule(
        MemoryLeakRule()
    )

    evaluation_engine = RootCauseEvaluationEngine()

    evaluation_engine.register_rule(
        MemoryIntensiveProcessEvaluationRule()
    )

    evaluation_engine.register_rule(
        MemoryLeakEvaluationRule()
    )

    evaluation_pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    selection = RootCauseSelection()

    return RootCauseReasoning(
        candidate_engine=candidate_engine,
        evaluation_pipeline=evaluation_pipeline,
        selection=selection,
    )


def test_root_cause_reasoning_can_be_created():

    reasoning = create_reasoning_engine()

    assert reasoning is not None


def test_reasoning_generates_candidates_from_findings():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    assert len(result["candidates"]) == 2


def test_reasoning_evaluates_generated_candidates():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    assert len(result["evaluations"]) == 2


def test_reasoning_preserves_candidate_identity():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    candidates = result["candidates"]
    evaluations = result["evaluations"]

    for evaluation in evaluations:
        assert evaluation.candidate in candidates


def test_reasoning_can_select_supported_primary_cause():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    result = reasoning.analyze(findings)

    assert result["primary_cause"] is not None
    assert (
        result["primary_cause"].cause_type
        == "MEMORY_INTENSIVE_PROCESS"
    )


def test_reasoning_keeps_memory_leak_uncertain_without_growth():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    leak_evaluations = [
        evaluation
        for evaluation in result["evaluations"]
        if evaluation.candidate.cause_type == "MEMORY_LEAK"
    ]

    assert len(leak_evaluations) == 1
    assert leak_evaluations[0].assessment == "INSUFFICIENT"


def test_reasoning_can_support_memory_leak_with_growth():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
        create_memory_growth_finding(),
    ]

    result = reasoning.analyze(findings)

    leak_evaluations = [
        evaluation
        for evaluation in result["evaluations"]
        if evaluation.candidate.cause_type == "MEMORY_LEAK"
    ]

    assert len(leak_evaluations) == 1
    assert leak_evaluations[0].assessment == "SUPPORTED"


def test_reasoning_does_not_force_primary_cause_when_candidates_tie():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
        create_memory_growth_finding(),
    ]

    result = reasoning.analyze(findings)

    assert result["primary_cause"] is None


def test_reasoning_preserves_findings():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    assert result["findings"] is findings


def test_reasoning_does_not_modify_findings():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    original_findings = list(findings)

    reasoning.analyze(findings)

    assert findings == original_findings


def test_reasoning_result_contains_candidates_evaluations_and_primary_cause():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    assert "findings" in result
    assert "candidates" in result
    assert "evaluations" in result
    assert "primary_cause" in result


def test_reasoning_does_not_create_confidence():

    reasoning = create_reasoning_engine()

    findings = [
        create_memory_pressure_finding(),
    ]

    result = reasoning.analyze(findings)

    assert "confidence" not in result