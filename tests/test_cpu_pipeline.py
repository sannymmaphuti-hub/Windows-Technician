from engine.collectors.cpu_collector import CPUCollector
from engine.evidence_builder import EvidenceBuilder
from engine.diagnostic_engine import DiagnosticEngine
from engine.rules.cpu_rule import CPUUsageRule
from engine.rules.cpu_contributor_rule import CPUContributorRule


def test_cpu_evidence_reaches_diagnostic_engine():

    collector = CPUCollector()

    builder = EvidenceBuilder()

    builder.add_collector(collector)

    evidence = builder.build()

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())
    engine.add_rule(CPUContributorRule())

    result = engine.diagnose(
        evidence.get_all()
    )

    assert isinstance(result, dict)

    assert "status" in result
    assert "total_findings" in result
    assert "findings" in result


def test_cpu_pipeline_uses_real_cpu_evidence():

    collector = CPUCollector()

    builder = EvidenceBuilder()

    builder.add_collector(collector)

    evidence = builder.build()

    cpu_data = evidence.get("CPU")

    assert cpu_data is not None

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose(
        evidence.get_all()
    )

    assert isinstance(result["findings"], list)