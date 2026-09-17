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


def test_resource_contention_rule_matches_cpu_and_memory_findings():
    rule = ResourceContentionRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    assert rule.matches(findings) is True


def test_resource_contention_rule_does_not_match_memory_only():
    rule = ResourceContentionRule()

    findings = [
        create_memory_finding(),
    ]

    assert rule.matches(findings) is False


def test_resource_contention_rule_does_not_match_cpu_only():
    rule = ResourceContentionRule()

    findings = [
        create_cpu_finding(),
    ]

    assert rule.matches(findings) is False


def test_resource_contention_rule_ignores_unrelated_findings():
    rule = ResourceContentionRule()

    unrelated = Finding(
        finding_type="STORAGE_PRESSURE",
        category="STORAGE",
        severity="HIGH",
        description="Storage pressure is high.",
    )

    findings = [
        create_memory_finding(),
        unrelated,
    ]

    assert rule.matches(findings) is False


def test_resource_contention_rule_creates_correlation():
    rule = ResourceContentionRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    correlation = rule.create_correlation(findings)

    assert correlation.correlation_type == "RESOURCE_CONTENTION"
    assert correlation.findings == findings
    assert correlation.strength == "MEDIUM"


def test_resource_contention_rule_explanation_preserves_uncertainty():
    rule = ResourceContentionRule()

    findings = [
        create_memory_finding(),
        create_cpu_finding(),
    ]

    correlation = rule.create_correlation(findings)

    assert "may" in correlation.explanation.lower()
    assert "caused" not in correlation.explanation.lower()


def test_resource_contention_rule_preserves_finding_objects():
    rule = ResourceContentionRule()

    memory = create_memory_finding()
    cpu = create_cpu_finding()

    correlation = rule.create_correlation([memory, cpu])

    assert correlation.findings[0] is memory
    assert correlation.findings[1] is cpu