from engine.adaptive_diagnostic_result import (
    AdaptiveDiagnosticResult,
)
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_diagnostic_evidence_adapter import (
    NetworkDiagnosticEvidenceAdapter,
)
from engine.network_diagnostic_pipeline import (
    NetworkDiagnosticPipeline,
)


def synthesize_case(evidence):
    adaptive_result = AdaptiveDiagnosticResult(
        evidence=evidence,
        decisions=[],
        actions=[],
        steps=0,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()
    network_evidence = adapter.convert(adaptive_result)

    pipeline = NetworkDiagnosticPipeline()

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    return synthesizer.synthesize(network_evidence)


def test_healthy_network_scenario_produces_network_case():
    case = synthesize_case(
        {
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [
                        {
                            "type": "IPv4",
                            "address": "192.168.0.238",
                            "classification": "PRIVATE",
                        }
                    ],
                }
            ],
            "gateway": "192.168.0.1",
            "gateway_reachable": True,
            "internet_reachable": True,
            "dns_working": True,
        }
    )

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )

    assert case.observations

    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.candidates == []
    assert case.evaluations == []

    assert case.primary_cause is None
    assert case.confidences == []
    assert case.recommendations == []


def test_gateway_reachable_but_internet_unavailable_produces_reasoning():
    case = synthesize_case(
        {
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [
                        {
                            "type": "IPv4",
                            "address": "192.168.0.238",
                            "classification": "PRIVATE",
                        }
                    ],
                }
            ],
            "gateway": "192.168.0.1",
            "gateway_reachable": True,
            "internet_reachable": False,
            "dns_working": False,
        }
    )

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )

    assert case.observations
    assert case.signals
    assert case.findings
    assert case.candidates
    assert case.evaluations
    assert case.confidences

    assert case.primary_cause is not None


def test_no_usable_adapter_does_not_invent_active_adapter():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": False,
                    "addresses": [],
                }
            ]
        },
        decisions=[],
        actions=[],
        steps=0,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert "active_adapter" in evidence
    assert evidence["active_adapter"] is None


def test_scenario_integration_preserves_raw_adaptive_evidence():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [],
                }
            ],
            "gateway_reachable": True,
        },
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert evidence["adapters"][0]["name"] == "Wi-Fi"
    assert evidence["gateway_reachable"] is True