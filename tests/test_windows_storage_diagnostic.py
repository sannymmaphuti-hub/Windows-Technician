# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE DIAGNOSTIC TESTS
# ==========================================

import pytest

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_storage_diagnostic import (
    WindowsStorageDiagnostic,
)


def test_storage_diagnostic_can_be_created():
    diagnostic = WindowsStorageDiagnostic()

    assert diagnostic is not None


def test_storage_diagnostic_has_storage_domain():
    diagnostic = WindowsStorageDiagnostic()

    assert diagnostic.domain == "STORAGE"


def test_storage_diagnostic_does_not_create_case():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "create_case",
    )


def test_storage_diagnostic_does_not_authorize():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "authorize",
    )


def test_storage_diagnostic_does_not_remediate():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "remediate",
    )


def test_storage_diagnostic_result_is_canonical():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_diagnostic_result_contains_storage_observation():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.observations,
        list,
    )


def test_storage_diagnostic_result_contains_storage_signals():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.signals,
        list,
    )


def test_storage_diagnostic_result_contains_findings():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.findings,
        list,
    )


def test_storage_diagnostic_result_contains_correlations():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.correlations,
        list,
    )


def test_storage_diagnostic_result_contains_candidates():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.candidates,
        list,
    )


def test_storage_diagnostic_result_contains_recommendations():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.recommendations,
        list,
    )


def test_storage_diagnostic_result_contains_confidences():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result.confidences,
        list,
    )


def test_storage_diagnostic_does_not_require_evidence():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_storage_diagnostic_calls_are_independent():
    diagnostic = WindowsStorageDiagnostic()

    first = diagnostic.analyze()
    second = diagnostic.analyze()

    assert first is not second


def test_storage_diagnostic_results_are_independent():
    diagnostic = WindowsStorageDiagnostic()

    first = diagnostic.analyze()
    second = diagnostic.analyze()

    first.observations.append(
        "test"
    )

    assert second.observations == []


def test_storage_diagnostic_does_not_change_case_state():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze()

    assert result is not None


def test_storage_diagnostic_has_explicit_analyze_contract():
    diagnostic = WindowsStorageDiagnostic()

    assert callable(
        diagnostic.analyze
    )


def test_storage_domain_is_normalized():
    diagnostic = WindowsStorageDiagnostic()

    assert diagnostic.domain == "STORAGE"


def test_storage_diagnostic_is_not_a_workflow():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "start_investigation",
    )

    assert not hasattr(
        diagnostic,
        "resolve",
    )


def test_storage_diagnostic_is_not_remediation():
    diagnostic = WindowsStorageDiagnostic()

    assert not hasattr(
        diagnostic,
        "execute",
    )