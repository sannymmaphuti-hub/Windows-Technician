from engine.finding import Finding
from engine.root_cause_engine import RootCauseEngine
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


def test_resource_contention_rule_integrates_with_root_cause_engine():
    engine = RootCauseEngine()
    engine.register_rule(ResourceContentionRootCauseRule())

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    candidates = engine.detect(findings)

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.cause_type == "RESOURCE_CONTENTION"
    assert candidate.category == "SYSTEM"


def test_root_cause_engine_does_not_create_contention_without_both_domains():
    engine = RootCauseEngine()
    engine.register_rule(ResourceContentionRootCauseRule())

    candidates = engine.detect([
        create_memory_finding(),
    ])

    assert candidates == []


def test_root_cause_engine_preserves_existing_rule_contract():
    engine = RootCauseEngine()
    rule = ResourceContentionRootCauseRule()

    engine.register_rule(rule)

    assert rule in engine._rules