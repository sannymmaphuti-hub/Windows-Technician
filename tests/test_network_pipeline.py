from engine.collectors.network_collector import NetworkCollector
from engine.evidence_builder import EvidenceBuilder
from engine.rules.network_rule import NetworkAdapterRule
from engine.diagnostic_engine import DiagnosticEngine


def test_network_pipeline():

    collector = NetworkCollector()

    network_data = collector.collect()

    builder = EvidenceBuilder()

    builder.add_category(
        "NETWORK",
        network_data
    )

    evidence = builder.build()

    engine = DiagnosticEngine()

    engine.add_rule(NetworkAdapterRule())

    result = engine.diagnose(
        evidence.get_all()
    )

    assert isinstance(result, dict)
    assert "status" in result
    assert "findings" in result
    assert "total_findings" in result