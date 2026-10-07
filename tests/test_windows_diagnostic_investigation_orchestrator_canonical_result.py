# ==========================================
# Windows Technician v0.9
# WINDOWS DIAGNOSTIC INVESTIGATION
# ORCHESTRATOR CANONICAL RESULT TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_investigation_orchestrator import (
    WindowsDiagnosticInvestigationOrchestrator,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)


class FakeDispatcher:

    def __init__(self, result):
        self.result = result

    def dispatch(self, domain, evidence=None):
        return self.result


def test_orchestrator_uses_canonical_result_for_dictionary_output():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher(
        {
            "observations": ["observation"],
            "signals": ["signal"],
            "findings": ["finding"],
        }
    )

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert result is case
    assert case.observations == ["observation"]
    assert case.signals == ["signal"]
    assert case.findings == ["finding"]


def test_orchestrator_accepts_existing_canonical_result():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    diagnostic_result = WindowsDiagnosticResult(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
    )

    orchestrator.dispatcher = FakeDispatcher(
        diagnostic_result
    )

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert result is case
    assert case.observations == ["observation"]
    assert case.signals == ["signal"]
    assert case.findings == ["finding"]


def test_orchestrator_does_not_replace_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher(
        {
            "findings": ["finding"],
        }
    )

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert result is case


def test_orchestrator_preserves_case_identity():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher(
        {
            "findings": ["finding"],
        }
    )

    case = DiagnosticCase()
    original_case_id = case.case_id

    orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert case.case_id == original_case_id


def test_orchestrator_preserves_case_lifecycle():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher(
        {
            "findings": ["finding"],
        }
    )

    case = DiagnosticCase()
    original_lifecycle = case.lifecycle_state

    orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert case.lifecycle_state == original_lifecycle


def test_orchestrator_preserves_case_status():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher(
        {
            "findings": ["finding"],
        }
    )

    case = DiagnosticCase()
    original_status = case.status

    orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert case.status == original_status


def test_orchestrator_normalizes_legacy_dictionary_before_attachment():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    legacy_result = {
        "observations": ["observation"],
        "signals": ["signal"],
        "findings": ["finding"],
        "correlations": ["correlation"],
        "candidates": ["candidate"],
        "primary_cause": "cause",
        "recommendations": ["recommendation"],
        "confidences": ["HIGH"],
    }

    orchestrator.dispatcher = FakeDispatcher(
        legacy_result
    )

    case = DiagnosticCase()

    orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert case.observations == [
        "observation"
    ]
    assert case.signals == [
        "signal"
    ]
    assert case.findings == [
        "finding"
    ]
    assert case.correlations == [
        "correlation"
    ]
    assert case.root_cause_candidates == [
        "candidate"
    ]
    assert case.primary_root_cause == "cause"
    assert case.recommendations == [
        "recommendation"
    ]


def test_orchestrator_accepts_case_with_empty_result():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.dispatcher = FakeDispatcher({})

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="PROCESS",
    )

    assert result is case
    assert case.observations == []
    assert case.signals == []
    assert case.findings == []


def test_orchestrator_rejects_invalid_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    try:
        orchestrator.investigate(
            case="invalid",
            domain="PROCESS",
        )
    except ValueError as error:
        assert str(error) == (
            "investigate requires a DiagnosticCase."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_orchestrator_rejects_missing_domain():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    try:
        orchestrator.investigate(
            case=case,
            domain=None,
        )
    except ValueError as error:
        assert str(error) == (
            "investigate requires a diagnostic domain."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_orchestrator_does_not_authorize_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "authorize",
    )


def test_orchestrator_does_not_execute_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "remediate",
    )


def test_orchestrator_does_not_create_cases():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    assert not hasattr(
        orchestrator,
        "create_case",
    )