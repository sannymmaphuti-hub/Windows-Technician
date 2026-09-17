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


def create_adaptive_network_result():
    return AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "speed_mbps": 100,
                    "addresses": [
                        {
                            "type": "IPv4",
                            "address": "192.168.0.238",
                            "netmask": "255.255.255.0",
                            "broadcast": "192.168.0.255",
                            "classification": "PRIVATE",
                        }
                    ],
                }
            ],
            "gateway": "192.168.0.1",
            "gateway_reachable": True,
            "internet_reachable": False,
            "dns_working": False,
        },
        decisions=[
            "CHECK_NETWORK_ADAPTER",
            "CHECK_GATEWAY_REACHABILITY",
            "CHECK_DNS_RESOLUTION",
            "CHECK_INTERNET_CONNECTIVITY",
        ],
        actions=[
            "COLLECT_NETWORK_ADAPTER_STATE",
            "PING_DEFAULT_GATEWAY",
            "TEST_DNS_RESOLUTION",
            "TEST_INTERNET_CONNECTIVITY",
        ],
        steps=4,
        stopped_reason="NO_DECISION",
    )


def test_adaptive_network_result_can_enter_v05_reasoning_pipeline():
    adaptive_result = create_adaptive_network_result()

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    pipeline = NetworkDiagnosticPipeline()

    result = pipeline.diagnose(evidence)

    assert isinstance(result, dict)

    assert result["observations"]
    assert result["signals"]
    assert result["findings"]
    assert isinstance(result["correlations"], list)
    assert result["candidates"]
    assert result["evaluations"]
    assert result["confidences"]


def test_adaptive_network_result_can_be_synthesized_into_case():
    adaptive_result = create_adaptive_network_result()

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    pipeline = NetworkDiagnosticPipeline()

    synthesizer = NetworkDiagnosticCaseSynthesizer(
        pipeline
    )

    case = synthesizer.synthesize(evidence)

    assert isinstance(
        case,
        NetworkDiagnosticCase,
    )

    assert case.observations
    assert case.signals
    assert case.findings
    assert isinstance(case.correlations, list)
    assert case.candidates
    assert case.evaluations
    assert case.confidences


def test_adaptive_network_integration_preserves_diagnostic_action_evidence():
    adaptive_result = create_adaptive_network_result()

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert evidence["gateway"] == "192.168.0.1"

    assert evidence["gateway_reachable"] is True
    assert evidence["dns_working"] is False
    assert evidence["internet_reachable"] is False

    assert evidence["active_adapter"]["name"] == "Wi-Fi"
    assert evidence["active_adapter"]["is_up"] is True


def test_adaptive_network_integration_does_not_create_reasoning():
    adaptive_result = create_adaptive_network_result()

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert "findings" not in evidence
    assert "correlations" not in evidence
    assert "candidates" not in evidence
    assert "evaluations" not in evidence
    assert "recommendations" not in evidence