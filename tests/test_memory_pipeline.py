from engine.collectors.memory_collector import MemoryCollector
from engine.evidence_builder import EvidenceBuilder
from engine.diagnostic_engine import DiagnosticEngine
from engine.rules.memory_rule import MemoryUsageRule


def test_memory_pipeline():

    collector = MemoryCollector()

    memory_data = collector.collect()

    builder = EvidenceBuilder()

    builder.add_category(
        "MEMORY",
        memory_data
    )

    evidence = builder.build()

    engine = DiagnosticEngine()

    engine.add_rule(MemoryUsageRule())

    result = engine.diagnose(
        evidence.get_all()
    )

    assert isinstance(result, dict)

    assert "status" in result

    assert "findings" in result

    assert "total_findings" in result