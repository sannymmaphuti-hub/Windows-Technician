from engine.finding import Finding
from engine.root_cause_rule import RootCauseRule
from engine.memory_intensive_process_rule import MemoryIntensiveProcessRule


def create_memory_finding():

    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
        supporting_signals=[],
    )


def test_memory_intensive_process_rule_is_a_root_cause_rule():

    rule = MemoryIntensiveProcessRule()

    assert isinstance(rule, RootCauseRule)


def test_memory_intensive_process_rule_matches_memory_pressure():

    rule = MemoryIntensiveProcessRule()

    findings = [
        create_memory_finding()
    ]

    assert rule.matches(findings) is True


def test_memory_intensive_process_rule_does_not_match_unrelated_findings():

    rule = MemoryIntensiveProcessRule()

    finding = Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
        supporting_signals=[],
    )

    assert rule.matches([finding]) is False


def test_memory_intensive_process_rule_creates_candidate():

    rule = MemoryIntensiveProcessRule()

    findings = [
        create_memory_finding()
    ]

    candidate = rule.create_candidate(findings)

    assert candidate.cause_type == "MEMORY_INTENSIVE_PROCESS"
    assert candidate.category == "MEMORY"


def test_memory_intensive_process_rule_candidate_expresses_uncertainty():

    rule = MemoryIntensiveProcessRule()

    candidate = rule.create_candidate(
        [create_memory_finding()]
    )

    assert "may" in candidate.explanation.lower()
    assert "possible" in candidate.explanation.lower()


def test_memory_intensive_process_rule_preserves_findings_as_input():

    rule = MemoryIntensiveProcessRule()

    finding = create_memory_finding()
    findings = [finding]

    candidate = rule.create_candidate(findings)

    assert findings == [finding]