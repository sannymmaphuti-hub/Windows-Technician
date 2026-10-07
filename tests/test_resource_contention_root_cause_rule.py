from engine.finding import Finding
from engine.resource_contention_root_cause_rule import (
    ResourceContentionRootCauseRule,
)


def create_memory_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def create_cpu_finding():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
    )


def create_storage_finding():
    return Finding(
        finding_type="STORAGE_PRESSURE",
        category="STORAGE",
        severity="HIGH",
        description="Storage pressure is high.",
    )


def test_resource_contention_root_cause_rule_matches_cpu_and_memory():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    assert rule.matches(findings) is True


def test_resource_contention_root_cause_rule_requires_cpu_pressure():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_memory_finding(),
    ]

    assert rule.matches(findings) is False


def test_resource_contention_root_cause_rule_requires_memory_pressure():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_cpu_finding(),
    ]

    assert rule.matches(findings) is False


def test_resource_contention_root_cause_rule_ignores_unrelated_findings():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_memory_finding(),
        create_storage_finding(),
    ]

    assert rule.matches(findings) is False


def test_resource_contention_root_cause_rule_creates_candidate():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    candidate = rule.create_candidate(findings)

    assert candidate.cause_type == "RESOURCE_CONTENTION"
    assert candidate.category == "SYSTEM"


def test_resource_contention_root_cause_rule_explanation_preserves_uncertainty():
    rule = ResourceContentionRootCauseRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    candidate = rule.create_candidate(findings)

    assert "may" in candidate.explanation.lower()
    assert "caused" not in candidate.explanation.lower()