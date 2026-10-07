from engine.cpu_resource_demand_root_cause_rule import (
    CpuResourceDemandRootCauseRule,
)
from engine.finding import Finding
from engine.root_cause_engine import RootCauseEngine


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


def test_cpu_resource_demand_integrates_with_root_cause_engine():
    engine = RootCauseEngine()

    rule = CpuResourceDemandRootCauseRule()
    engine.register_rule(rule)

    candidates = engine.detect([
        create_cpu_pressure(),
    ])

    assert len(candidates) == 1

    candidate = candidates[0]

    assert candidate.cause_type == "CPU_RESOURCE_DEMAND"
    assert candidate.category == "CPU"


def test_cpu_resource_demand_does_not_trigger_without_cpu_pressure():
    engine = RootCauseEngine()

    engine.register_rule(
        CpuResourceDemandRootCauseRule()
    )

    candidates = engine.detect([
        create_memory_pressure(),
    ])

    assert candidates == []


def test_cpu_resource_demand_can_coexist_with_cross_domain_findings():
    engine = RootCauseEngine()

    engine.register_rule(
        CpuResourceDemandRootCauseRule()
    )

    candidates = engine.detect([
        create_cpu_pressure(),
        create_memory_pressure(),
    ])

    assert len(candidates) == 1
    assert candidates[0].cause_type == "CPU_RESOURCE_DEMAND"