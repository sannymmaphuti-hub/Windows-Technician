# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC RESULT NORMALIZER TESTS
# ==========================================

import pytest

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_diagnostic_result_normalizer import (
    WindowsDiagnosticResultNormalizer,
)


def test_normalizer_accepts_canonical_result():
    result = WindowsDiagnosticResult(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
    )

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized is result


def test_normalizer_converts_dictionary_result():
    result = {
        "observations": ["observation"],
        "signals": ["signal"],
        "findings": ["finding"],
        "correlations": ["correlation"],
        "candidates": ["candidate"],
        "primary_cause": "cause",
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert isinstance(
        normalized,
        WindowsDiagnosticResult,
    )


def test_dictionary_observations_are_normalized():
    result = {
        "observations": ["observation"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.observations == [
        "observation"
    ]


def test_dictionary_signals_are_normalized():
    result = {
        "signals": ["signal"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.signals == [
        "signal"
    ]


def test_dictionary_findings_are_normalized():
    result = {
        "findings": ["finding"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.findings == [
        "finding"
    ]


def test_dictionary_correlations_are_normalized():
    result = {
        "correlations": ["correlation"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.correlations == [
        "correlation"
    ]


def test_dictionary_candidates_are_normalized():
    result = {
        "candidates": ["candidate"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.candidates == [
        "candidate"
    ]


def test_dictionary_primary_cause_is_normalized():
    result = {
        "primary_cause": "cause"
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.primary_cause == "cause"


def test_dictionary_recommendations_are_normalized():
    result = {
        "recommendations": ["recommendation"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.recommendations == [
        "recommendation"
    ]


def test_dictionary_confidences_are_normalized():
    result = {
        "confidences": ["HIGH"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            result
        )
    )

    assert normalized.confidences == [
        "HIGH"
    ]


def test_missing_dictionary_fields_use_empty_defaults():
    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            {}
        )
    )

    assert normalized.observations == []
    assert normalized.signals == []
    assert normalized.findings == []
    assert normalized.correlations == []
    assert normalized.candidates == []
    assert normalized.primary_cause is None
    assert normalized.recommendations == []
    assert normalized.confidences == []


def test_none_is_rejected():
    with pytest.raises(ValueError):
        WindowsDiagnosticResultNormalizer.normalize(
            None
        )


def test_unsupported_result_type_is_rejected():
    with pytest.raises(ValueError):
        WindowsDiagnosticResultNormalizer.normalize(
            "invalid"
        )


def test_normalizer_returns_independent_result_for_dictionary():
    source = {
        "findings": ["finding"]
    }

    normalized = (
        WindowsDiagnosticResultNormalizer.normalize(
            source
        )
    )

    source["findings"].append("later")

    assert normalized.findings == [
        "finding"
    ]


def test_normalizer_does_not_execute_diagnostics():
    assert not hasattr(
        WindowsDiagnosticResultNormalizer,
        "diagnose",
    )

    assert not hasattr(
        WindowsDiagnosticResultNormalizer,
        "execute",
    )


def test_normalizer_does_not_create_cases():
    assert not hasattr(
        WindowsDiagnosticResultNormalizer,
        "create_case",
    )


def test_normalizer_does_not_authorize_remediation():
    assert not hasattr(
        WindowsDiagnosticResultNormalizer,
        "authorize",
    )


def test_normalizer_does_not_execute_remediation():
    assert not hasattr(
        WindowsDiagnosticResultNormalizer,
        "remediate",
    )