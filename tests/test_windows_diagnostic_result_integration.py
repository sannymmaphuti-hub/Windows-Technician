# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC RESULT INTEGRATION TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_diagnostic_investigation_coordinator import (
    WindowsDiagnosticInvestigationCoordinator,
)


def test_coordinator_accepts_canonical_diagnostic_result():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
        correlations=["correlation"],
        candidates=["candidate"],
        primary_cause="primary",
        recommendations=["recommendation"],
        confidences=["HIGH"],
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    returned_case = coordinator.attach_result(
        case,
        result,
    )

    assert returned_case is case


def test_canonical_result_observations_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        observations=["observation"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.observations == ["observation"]


def test_canonical_result_signals_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        signals=["signal"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.signals == ["signal"]


def test_canonical_result_findings_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        findings=["finding"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.findings == ["finding"]


def test_canonical_result_correlations_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        correlations=["correlation"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.correlations == ["correlation"]


def test_canonical_result_candidates_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        candidates=["candidate"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.root_cause_candidates == ["candidate"]


def test_canonical_result_primary_cause_is_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        primary_cause="primary"
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.primary_root_cause == "primary"


def test_canonical_result_recommendations_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        recommendations=["recommendation"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.recommendations == ["recommendation"]


def test_canonical_result_does_not_alias_case_collections():
    case = DiagnosticCase()

    observations = ["observation"]

    result = WindowsDiagnosticResult(
        observations=observations
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    observations.append("later")

    assert case.observations == ["observation"]


def test_canonical_result_does_not_alias_case_primary_cause():
    case = DiagnosticCase()

    primary_cause = {
        "cause": "memory pressure"
    }

    result = WindowsDiagnosticResult(
        primary_cause=primary_cause
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    primary_cause["cause"] = "changed"

    assert case.primary_root_cause == {
        "cause": "memory pressure"
    }


def test_canonical_result_empty_values_are_attached():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult()

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.observations == []
    assert case.signals == []
    assert case.findings == []
    assert case.correlations == []
    assert case.root_cause_candidates == []
    assert case.primary_root_cause is None


def test_canonical_result_does_not_change_case_lifecycle():
    case = DiagnosticCase()
    original_lifecycle = case.lifecycle_state

    result = WindowsDiagnosticResult(
        findings=["finding"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert case.lifecycle_state == original_lifecycle


def test_canonical_result_does_not_authorize_remediation():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        recommendations=["recommendation"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert not hasattr(
        case,
        "authorization"
    )


def test_canonical_result_does_not_execute_remediation():
    case = DiagnosticCase()

    result = WindowsDiagnosticResult(
        recommendations=["recommendation"]
    )

    coordinator = (
        WindowsDiagnosticInvestigationCoordinator()
    )

    coordinator.attach_result(case, result)

    assert not hasattr(
        case,
        "remediation_result"
    )


def test_canonical_result_is_the_only_new_result_boundary():
    result = WindowsDiagnosticResult(
        observations=["o"],
        signals=["s"],
        findings=["f"],
        correlations=["c"],
        candidates=["candidate"],
        primary_cause="cause",
        recommendations=["recommendation"],
        confidences=["HIGH"],
    )

    assert result.observations == ["o"]
    assert result.signals == ["s"]
    assert result.findings == ["f"]
    assert result.correlations == ["c"]
    assert result.candidates == ["candidate"]
    assert result.primary_cause == "cause"
    assert result.recommendations == ["recommendation"]
    assert result.confidences == ["HIGH"]