from engine.adaptive_diagnostic_result import (
    AdaptiveDiagnosticResult,
)
from engine.network_diagnostic_evidence_adapter import (
    NetworkDiagnosticEvidenceAdapter,
)


def test_adapter_converts_adaptive_network_evidence():
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

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert evidence["active_adapter"]["name"] == "Wi-Fi"
    assert evidence["active_adapter"]["is_up"] is True

    assert evidence["gateway"] == "192.168.0.1"
    assert evidence["gateway_reachable"] is True
    assert evidence["internet_reachable"] is False
    assert evidence["dns_working"] is False


def test_adapter_does_not_create_diagnostic_conclusions():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [],
                }
            ]
        },
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert "findings" not in evidence
    assert "correlations" not in evidence
    assert "root_causes" not in evidence
    assert "recommendations" not in evidence

def test_adapter_rejects_wrong_input_type():
    adapter = NetworkDiagnosticEvidenceAdapter()

    try:
        adapter.convert({})
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_adapter_rejects_non_list_network_adapters():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": "not-a-list",
        },
        decisions=[],
        actions=[],
        steps=0,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    try:
        adapter.convert(adaptive_result)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_adapter_does_not_select_adapter_without_valid_ipv4():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [],
                }
            ]
        },
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert evidence["active_adapter"] is None


def test_adapter_does_not_select_adapter_with_invalid_ipv4():
    adaptive_result = AdaptiveDiagnosticResult(
        evidence={
            "adapters": [
                {
                    "name": "Wi-Fi",
                    "is_up": True,
                    "addresses": [
                        {
                            "type": "IPv4",
                            "address": "169.254.10.20",
                            "classification": "APIPA",
                        }
                    ],
                }
            ]
        },
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    assert evidence["active_adapter"] is None


def test_adapter_does_not_mutate_adaptive_evidence():
    original_evidence = {
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
    }

    adaptive_result = AdaptiveDiagnosticResult(
        evidence=original_evidence,
        decisions=[],
        actions=[],
        steps=1,
        stopped_reason="NO_DECISION",
    )

    adapter = NetworkDiagnosticEvidenceAdapter()

    evidence = adapter.convert(adaptive_result)

    evidence["active_adapter"]["name"] = "CHANGED"

    assert (
        adaptive_result.evidence["adapters"][0]["name"]
        == "Wi-Fi"
    )