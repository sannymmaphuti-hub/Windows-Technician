from engine.finding import Finding
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_evaluation_rule import RootCauseEvaluationRule
from engine.memory_intensive_process_evaluation_rule import (
    MemoryIntensiveProcessEvaluationRule,
)


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the observed memory pressure."
        ),
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
            "A specific process is consuming an unusually "
            "large amount of system memory."
        ),
        supporting_signals=[],
    )


def test_rule_matches_when_memory_pressure_and_process_evidence_exist():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    assert rule.matches(
        create_candidate(),
        findings,
    )


def test_process_evidence_improves_assessment():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert evaluation.assessment == "SUPPORTED"


def test_evaluation_preserves_process_evidence():

    rule = MemoryIntensiveProcessEvaluationRule()

    process_finding = create_process_memory_finding()

    findings = [
        create_memory_pressure_finding(),
        process_finding,
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert process_finding in evaluation.supporting_evidence


def test_evaluation_preserves_memory_pressure_evidence():

    rule = MemoryIntensiveProcessEvaluationRule()

    memory_finding = create_memory_pressure_finding()

    findings = [
        memory_finding,
        create_process_memory_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert memory_finding in evaluation.supporting_evidence


def test_evaluation_explains_process_evidence():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    explanation = evaluation.explanation.lower()

    assert "process" in explanation
    assert "memory" in explanation
    assert "supports" in explanation


def test_evaluation_remains_uncertain():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    explanation = evaluation.explanation.lower()

    assert (
        "may" in explanation
        or "possible" in explanation
        or "suggest" in explanation
        or "supports" in explanation
    )


def test_evaluation_does_not_select_primary_cause():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )


def test_unrelated_cpu_finding_does_not_replace_process_evidence():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_memory_pressure_finding(),
        create_process_memory_finding(),
        Finding(
            finding_type="CPU_PRESSURE",
            category="CPU",
            severity="HIGH",
            description="System CPU pressure is high.",
            supporting_signals=[],
        ),
    ]

    evaluation = rule.create_evaluation(
        create_candidate(),
        findings,
    )

    assert evaluation.assessment == "SUPPORTED"


def test_rule_still_requires_memory_pressure():

    rule = MemoryIntensiveProcessEvaluationRule()

    findings = [
        create_process_memory_finding(),
    ]

    assert not rule.matches(
        create_candidate(),
        findings,
    )