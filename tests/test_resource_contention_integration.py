from engine.correlation_engine import CorrelationEngine
from engine.finding import Finding
from engine.resource_contention_rule import ResourceContentionRule


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


def test_correlation_engine_detects_resource_contention():
    engine = CorrelationEngine()
    engine.register_rule(ResourceContentionRule())

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    correlations = engine.detect(findings)

    assert len(correlations) == 1
    assert correlations[0].correlation_type == "RESOURCE_CONTENTION"


def test_correlation_engine_returns_no_resource_contention_for_memory_only():
    engine = CorrelationEngine()
    engine.register_rule(ResourceContentionRule())

    findings = [
        create_memory_finding(),
    ]

    correlations = engine.detect(findings)

    assert correlations == []


def test_correlation_engine_returns_no_resource_contention_for_cpu_only():
    engine = CorrelationEngine()
    engine.register_rule(ResourceContentionRule())

    findings = [
        create_cpu_finding(),
    ]

    correlations = engine.detect(findings)

    assert correlations == []


def test_resource_contention_correlation_preserves_findings():
    engine = CorrelationEngine()
    engine.register_rule(ResourceContentionRule())

    memory = create_memory_finding()
    cpu = create_cpu_finding()

    findings = [memory, cpu]

    correlations = engine.detect(findings)

    assert correlations[0].findings[0] is memory
    assert correlations[0].findings[1] is cpu

def test_resource_contention_is_detected_when_unrelated_findings_are_present():
    engine = CorrelationEngine()
    engine.register_rule(ResourceContentionRule())

    storage = Finding(
        finding_type="STORAGE_PRESSURE",
        category="STORAGE",
        severity="HIGH",
        description="Storage pressure is high.",
    )

    findings = [
        create_memory_finding(),
        storage,
        create_cpu_finding(),
    ]

    correlations = engine.detect(findings)

    assert len(correlations) == 1
    assert correlations[0].correlation_type == "RESOURCE_CONTENTION"