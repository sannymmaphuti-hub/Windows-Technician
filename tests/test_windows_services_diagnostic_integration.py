# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES DIAGNOSTIC INTEGRATION
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.windows_diagnostic_investigation_orchestrator import (
    WindowsDiagnosticInvestigationOrchestrator,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


def make_evidence(services):
    return WindowsServicesEvidence(
        services=services
    )


def test_services_can_be_dispatched_without_evidence():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    result = orchestrator.investigate(
        case=case,
        domain="SERVICES",
    )

    assert result is case
    assert case.observations == []
    assert case.signals == []
    assert case.findings == []
    assert case.recommendations == []


def test_services_can_be_investigated_with_evidence():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "display_name": "Print Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert result is case


def test_services_signal_reaches_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert len(case.signals) == 1
    assert (
        case.signals[0].signal_type
        == "SERVICE_STOPPED"
    )


def test_services_finding_reaches_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert len(case.findings) == 1
    assert (
        case.findings[0].finding_type
        == "SERVICE_UNAVAILABLE"
    )


def test_services_recommendation_reaches_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert len(case.recommendations) == 1
    assert (
        case.recommendations[0]
        .recommendation_type
        == "REVIEW_SERVICE_STATE"
    )


def test_services_finding_preserves_signal_identity():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert (
        case.findings[0].supporting_signals[0]
        is case.signals[0]
    )


def test_services_disabled_finding_reaches_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "DISABLED",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert len(case.signals) == 1
    assert (
        case.signals[0].signal_type
        == "SERVICE_DISABLED"
    )

    assert len(case.findings) == 1
    assert (
        case.findings[0].finding_type
        == "SERVICE_DISABLED"
    )


def test_healthy_service_produces_no_case_findings():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "RUNNING",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert case.signals == []
    assert case.findings == []
    assert case.recommendations == []


def test_non_required_stopped_service_produces_no_case_finding():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "OptionalService",
                "status": "STOPPED",
                "start_type": "MANUAL",
                "required": False,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert case.signals == []
    assert case.findings == []
    assert case.recommendations == []


def test_services_investigation_does_not_authorize():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert not hasattr(
        case,
        "authorization",
    )

    assert not hasattr(
        case,
        "authorized",
    )


def test_services_investigation_does_not_execute_remediation():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert not hasattr(
        case,
        "execution_status",
    )

    assert not hasattr(
        case,
        "remediation_result",
    )


def test_services_investigation_requires_diagnostic_case():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    try:
        orchestrator.investigate(
            case=None,
            domain="SERVICES",
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for missing case."
    )


def test_services_invalid_evidence_is_rejected():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    try:
        orchestrator.investigate(
            case=case,
            domain="SERVICES",
            evidence=None,
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for explicit None evidence."
    )


def test_services_case_remains_same_instance():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = orchestrator.investigate(
        case=case,
        domain="SERVICES",
        evidence=evidence,
    )

    assert result is case


def test_services_result_is_canonical_before_case_attachment():
    orchestrator = (
        WindowsDiagnosticInvestigationOrchestrator()
    )

    case = DiagnosticCase()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    raw_result = (
        orchestrator.dispatcher.dispatch(
            "SERVICES",
            evidence=evidence,
        )
    )

    assert isinstance(
        raw_result,
        WindowsDiagnosticResult,
    )