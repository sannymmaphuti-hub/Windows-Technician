# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC RESULT TESTS
# ==========================================


from copy import deepcopy

import pytest

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)


def test_result_can_be_created():
    result = WindowsDiagnosticResult()

    assert result is not None


def test_result_has_observations():
    result = WindowsDiagnosticResult(
        observations=[
            {
                "category": "NETWORK",
            }
        ]
    )

    assert result.observations == [
        {
            "category": "NETWORK",
        }
    ]


def test_result_has_signals():
    result = WindowsDiagnosticResult(
        signals=[
            {
                "name": "NETWORK_DISCONNECTED",
            }
        ]
    )

    assert result.signals == [
        {
            "name": "NETWORK_DISCONNECTED",
        }
    ]


def test_result_has_findings():
    result = WindowsDiagnosticResult(
        findings=[
            {
                "severity": "WARNING",
            }
        ]
    )

    assert result.findings == [
        {
            "severity": "WARNING",
        }
    ]


def test_result_has_correlations():
    result = WindowsDiagnosticResult(
        correlations=[
            {
                "type": "NETWORK_FAILURE",
            }
        ]
    )

    assert result.correlations == [
        {
            "type": "NETWORK_FAILURE",
        }
    ]


def test_result_has_root_cause_candidates():
    result = WindowsDiagnosticResult(
        candidates=[
            {
                "category": "NETWORK",
            }
        ]
    )

    assert result.candidates == [
        {
            "category": "NETWORK",
        }
    ]


def test_result_has_primary_root_cause():
    primary_cause = {
        "category": "NETWORK",
        "explanation": "Network connectivity is unavailable.",
    }

    result = WindowsDiagnosticResult(
        primary_cause=primary_cause
    )

    assert result.primary_cause == primary_cause


def test_result_has_recommendations():
    result = WindowsDiagnosticResult(
        recommendations=[
            {
                "action": "CHECK_NETWORK_ADAPTER",
            }
        ]
    )

    assert result.recommendations == [
        {
            "action": "CHECK_NETWORK_ADAPTER",
        }
    ]


def test_result_has_confidences():
    result = WindowsDiagnosticResult(
        confidences=[
            {
                "score": 0.92,
            }
        ]
    )

    assert result.confidences == [
        {
            "score": 0.92,
        }
    ]


def test_missing_collections_default_to_empty():
    result = WindowsDiagnosticResult()

    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.recommendations == []
    assert result.confidences == []


def test_missing_primary_cause_defaults_to_none():
    result = WindowsDiagnosticResult()

    assert result.primary_cause is None


def test_collections_are_defensively_copied():
    observations = [
        {
            "category": "NETWORK",
        }
    ]

    result = WindowsDiagnosticResult(
        observations=observations
    )

    observations.append(
        {
            "category": "MEMORY",
        }
    )

    assert result.observations == [
        {
            "category": "NETWORK",
        }
    ]


def test_nested_data_is_defensively_copied():
    findings = [
        {
            "details": {
                "severity": "WARNING",
            }
        }
    ]

    result = WindowsDiagnosticResult(
        findings=findings
    )

    findings[0]["details"]["severity"] = "CRITICAL"

    assert (
        result.findings[0]["details"]["severity"]
        == "WARNING"
    )


def test_primary_cause_is_defensively_copied():
    primary_cause = {
        "details": {
            "category": "NETWORK",
        }
    }

    result = WindowsDiagnosticResult(
        primary_cause=primary_cause
    )

    primary_cause["details"]["category"] = "MEMORY"

    assert (
        result.primary_cause["details"]["category"]
        == "NETWORK"
    )


def test_result_does_not_execute_diagnostics():
    result = WindowsDiagnosticResult()

    assert not hasattr(
        result,
        "diagnose",
    )

    assert not hasattr(
        result,
        "execute",
    )

    assert not hasattr(
        result,
        "analyze",
    )


def test_result_does_not_create_cases():
    result = WindowsDiagnosticResult()

    assert not hasattr(
        result,
        "case",
    )

    assert not hasattr(
        result,
        "diagnostic_case",
    )


def test_result_does_not_authorize_remediation():
    result = WindowsDiagnosticResult()

    assert not hasattr(
        result,
        "authorized",
    )

    assert not hasattr(
        result,
        "authorization_status",
    )


def test_result_does_not_execute_remediation():
    result = WindowsDiagnosticResult()

    assert not hasattr(
        result,
        "execute_remediation",
    )

    assert not hasattr(
        result,
        "remediation_result",
    )


def test_result_does_not_manage_workflow():
    result = WindowsDiagnosticResult()

    assert not hasattr(
        result,
        "workflow",
    )

    assert not hasattr(
        result,
        "technician_workflow",
    )


def test_result_can_represent_empty_diagnosis():
    result = WindowsDiagnosticResult()

    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.primary_cause is None
    assert result.recommendations == []
    assert result.confidences == []


def test_result_can_represent_complete_diagnosis():
    result = WindowsDiagnosticResult(
        observations=[
            {
                "category": "NETWORK",
            }
        ],
        signals=[
            {
                "name": "NETWORK_DISCONNECTED",
            }
        ],
        findings=[
            {
                "severity": "WARNING",
            }
        ],
        correlations=[
            {
                "type": "NETWORK_FAILURE",
            }
        ],
        candidates=[
            {
                "category": "NETWORK",
            }
        ],
        primary_cause={
            "category": "NETWORK",
        },
        recommendations=[
            {
                "action": "CHECK_NETWORK_ADAPTER",
            }
        ],
        confidences=[
            {
                "score": 0.92,
            }
        ],
    )

    assert result.observations
    assert result.signals
    assert result.findings
    assert result.correlations
    assert result.candidates
    assert result.primary_cause
    assert result.recommendations
    assert result.confidences


def test_result_accepts_none_collections_as_empty():
    result = WindowsDiagnosticResult(
        observations=None,
        signals=None,
        findings=None,
        correlations=None,
        candidates=None,
        recommendations=None,
        confidences=None,
    )

    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.recommendations == []
    assert result.confidences == []


def test_result_is_independent_between_instances():
    first = WindowsDiagnosticResult(
        findings=[
            {
                "severity": "WARNING",
            }
        ]
    )

    second = WindowsDiagnosticResult()

    assert first.findings != second.findings

    second.findings.append(
        {
            "severity": "CRITICAL",
        }
    )

    assert len(first.findings) == 1
    assert len(second.findings) == 1


def test_result_preserves_primary_cause_none():
    result = WindowsDiagnosticResult(
        primary_cause=None
    )

    assert result.primary_cause is None