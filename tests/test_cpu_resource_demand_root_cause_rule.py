from engine.cpu_resource_demand_root_cause_rule import (
    CpuResourceDemandRootCauseRule,
)
from engine.finding import Finding


def create_cpu_pressure():
    return Finding(
        finding_type="CPU_PRESSURE",
        category="CPU",
        severity="HIGH",
        description="System CPU pressure is high.",
    )


def create_memory_pressure():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="System memory pressure is high.",
    )


def test_cpu_resource_demand_rule_matches_cpu_pressure():
    rule = CpuResourceDemandRootCauseRule()

    assert rule.matches([
        create_cpu_pressure(),
    ]) is True


def test_cpu_resource_demand_rule_does_not_match_memory_only():
    rule = CpuResourceDemandRootCauseRule()

    assert rule.matches([
        create_memory_pressure(),
    ]) is False


def test_cpu_resource_demand_rule_matches_cpu_with_other_findings():
    rule = CpuResourceDemandRootCauseRule()

    assert rule.matches([
        create_cpu_pressure(),
        create_memory_pressure(),
    ]) is True


def test_cpu_resource_demand_rule_creates_candidate():
    rule = CpuResourceDemandRootCauseRule()

    candidate = rule.create_candidate([
        create_cpu_pressure(),
    ])

    assert candidate.cause_type == "CPU_RESOURCE_DEMAND"
    assert candidate.category == "CPU"


def test_cpu_resource_demand_explanation_preserves_uncertainty():
    rule = CpuResourceDemandRootCauseRule()

    candidate = rule.create_candidate([
        create_cpu_pressure(),
    ])

    explanation = candidate.explanation.lower()

    assert "may" in explanation
    assert "caused" not in explanation