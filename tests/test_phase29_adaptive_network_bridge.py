from engine.adaptive_diagnostic_result import (
    AdaptiveDiagnosticResult,
)
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_diagnostic_pipeline import (
    NetworkDiagnosticPipeline,
)


def test_adaptive_result_can_be_converted_to_network_case():
    adaptive_result = AdaptiveDiagnosticResult(
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
        decisions=[],
        actions=[],
        steps=4,
        stopped_reason="NO_DECISION",
    )

    pipeline = NetworkDiagnosticPipeline()
    synthesizer = NetworkDiagnosticCaseSynthesizer(pipeline)

    case = synthesizer.synthesize(
        adaptive_result.evidence
    )

    assert isinstance(case, NetworkDiagnosticCase)
    assert case.observations
    assert case.signals
    assert case.findings