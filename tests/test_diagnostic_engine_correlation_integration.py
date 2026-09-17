from engine.correlation_engine import CorrelationEngine
from engine.diagnostic_engine import DiagnosticEngine
from engine.finding import Finding
from engine.resource_contention_rule import ResourceContentionRule
from engine.rules.cpu_rule import CPUUsageRule
from engine.rules.memory_rule import MemoryUsageRule


def test_diagnostic_engine_correlates_legacy_findings_through_v05_adapter():

    correlation_engine = CorrelationEngine()

    correlation_engine.register_rule(
        ResourceContentionRule()
    )

    engine = DiagnosticEngine(
        correlation_engine=correlation_engine
    )

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 92
        },
        "MEMORY": {
            "usage_percent": 88
        }
    }

    result = engine.diagnose(evidence)

    assert len(result["findings"]) == 2

    assert all(
        isinstance(finding, dict)
        for finding in result["findings"]
    )

    assert len(result["correlations"]) == 1

    correlation = result["correlations"][0]

    assert correlation.correlation_type == "RESOURCE_CONTENTION"

    assert all(
        isinstance(finding, Finding)
        for finding in correlation.findings
    )


def test_diagnostic_engine_preserves_legacy_finding_output():

    correlation_engine = CorrelationEngine()

    correlation_engine.register_rule(
        ResourceContentionRule()
    )

    engine = DiagnosticEngine(
        correlation_engine=correlation_engine
    )

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())

    result = engine.diagnose(
        {
            "CPU": {
                "usage_percent": 92
            },
            "MEMORY": {
                "usage_percent": 88
            }
        }
    )

    assert isinstance(result["findings"], list)

    for finding in result["findings"]:
        assert isinstance(finding, dict)

        assert "category" in finding
        assert "severity" in finding
        assert "message" in finding