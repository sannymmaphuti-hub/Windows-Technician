# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP DIAGNOSTIC INTEGRATION TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_diagnostic_investigation_orchestrator import (
    WindowsDiagnosticInvestigationOrchestrator,
)
from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


def _evidence():
    return WindowsStartupEvidence(
        items=[
            {
                "name": "HealthyStartup",
                "command": "Healthy.exe",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
        ]
    )


def test_dispatcher_supports_startup():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    assert dispatcher.has_domain(
        "STARTUP"
    )


def test_dispatcher_returns_startup_adapter():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    adapter = dispatcher.get_adapter(
        "STARTUP"
    )

    assert adapter is not None
    assert adapter.domain == "STARTUP"


def test_dispatcher_can_execute_startup():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP",
        evidence=_evidence(),
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_dispatcher_detects_startup_problem():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP",
        evidence=_evidence(),
    )

    assert len(result.signals) == 1
    assert len(result.findings) == 1
    assert len(result.recommendations) == 1

    assert (
        result.signals[0].subject
        == "BrokenStartup"
    )


def test_dispatcher_preserves_signal_identity():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP",
        evidence=_evidence(),
    )

    assert (
        result.findings[0].supporting_signals[0]
        is result.signals[0]
    )


def test_orchestrator_attaches_startup_result():
    case = DiagnosticCase()

    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    returned_case = orchestrator.investigate(
        case,
        "STARTUP",
        evidence=_evidence(),
    )

    assert returned_case is case


def test_orchestrator_populates_case_signals():
    case = DiagnosticCase()

    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.investigate(
        case,
        "STARTUP",
        evidence=_evidence(),
    )

    assert len(case.signals) == 1
    assert (
        case.signals[0].subject
        == "BrokenStartup"
    )


def test_orchestrator_populates_case_findings():
    case = DiagnosticCase()

    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.investigate(
        case,
        "STARTUP",
        evidence=_evidence(),
    )

    assert len(case.findings) == 1
    assert (
        case.findings[0].finding_type
        == "STARTUP_COMMAND_MISSING"
    )


def test_orchestrator_populates_case_recommendations():
    case = DiagnosticCase()

    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.investigate(
        case,
        "STARTUP",
        evidence=_evidence(),
    )

    assert len(case.recommendations) == 1

    assert (
        case.recommendations[0]
        .recommendation_type
        == "REVIEW_STARTUP_ENTRY"
    )


def test_case_finding_preserves_signal_identity():
    case = DiagnosticCase()

    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    orchestrator.investigate(
        case,
        "STARTUP",
        evidence=_evidence(),
    )

    assert (
        case.findings[0].supporting_signals[0]
        is case.signals[0]
    )


def test_startup_does_not_create_remediation():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP",
        evidence=_evidence(),
    )

    assert not hasattr(
        result,
        "remediation_actions",
    )


def test_disabled_startup_is_not_reported():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "DisabledStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": False,
            }
        ]
    )

    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP",
        evidence=evidence,
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_invalid_startup_evidence_is_rejected():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    try:
        dispatcher.dispatch(
            "STARTUP",
            evidence=None,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for None evidence."
    )


def test_omitted_startup_evidence_remains_compatible():
    dispatcher = (
        WindowsDiagnosticDispatcher()
    )

    result = dispatcher.dispatch(
        "STARTUP"
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []