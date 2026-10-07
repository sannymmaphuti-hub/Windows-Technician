from engine.finding import Finding
from engine.memory_intensive_process_rule import MemoryIntensiveProcessRule


def create_memory_pressure():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def create_process_evidence():
    return Finding(
        finding_type="MEMORY_INTENSIVE_PROCESS",
        category="PROCESS",
        severity="HIGH",
        description="A process is consuming an unusually large amount of memory.",
    )


def create_cpu_pressure():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
    )


def test_memory_intensive_process_rule_matches_memory_pressure():
    rule = MemoryIntensiveProcessRule()

    assert rule.matches([
        create_memory_pressure(),
    ]) is True


def test_memory_intensive_process_rule_matches_process_evidence_with_memory_pressure():
    rule = MemoryIntensiveProcessRule()

    assert rule.matches([
        create_memory_pressure(),
        create_process_evidence(),
    ]) is True


def test_memory_intensive_process_rule_does_not_match_process_evidence_alone():
    rule = MemoryIntensiveProcessRule()

    assert rule.matches([
        create_process_evidence(),
    ]) is False


def test_memory_intensive_process_rule_ignores_unrelated_findings():
    rule = MemoryIntensiveProcessRule()

    assert rule.matches([
        create_memory_pressure(),
        create_cpu_pressure(),
    ]) is True


def test_memory_intensive_process_candidate_preserves_existing_identity():
    rule = MemoryIntensiveProcessRule()

    candidate = rule.create_candidate([
        create_memory_pressure(),
        create_process_evidence(),
    ])

    assert candidate.cause_type == "MEMORY_INTENSIVE_PROCESS"
    assert candidate.category == "MEMORY"


def test_memory_intensive_process_candidate_remains_uncertain():
    rule = MemoryIntensiveProcessRule()

    candidate = rule.create_candidate([
        create_memory_pressure(),
        create_process_evidence(),
    ])

    explanation = candidate.explanation.lower()

    assert "may" in explanation
    assert "caused" not in explanation