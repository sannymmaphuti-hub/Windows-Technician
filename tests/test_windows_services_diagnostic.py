# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES DIAGNOSTIC TESTS
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)

from engine.windows_services_diagnostic import (
    WindowsServicesDiagnostic,
)

from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


def test_domain():
    diagnostic = WindowsServicesDiagnostic()

    assert diagnostic.domain == "SERVICES"


def test_no_evidence_preserves_empty_result_contract():
    diagnostic = WindowsServicesDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_none_evidence_is_rejected():
    diagnostic = WindowsServicesDiagnostic()

    try:
        diagnostic.analyze(None)
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for None evidence."
    )


def test_invalid_evidence_is_rejected():
    diagnostic = WindowsServicesDiagnostic()

    try:
        diagnostic.analyze({})
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid evidence."
    )


def test_healthy_service_produces_empty_result():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "display_name": "Print Spooler",
                "status": "RUNNING",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_stopped_required_service_produces_signal():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "display_name": "Print Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert len(result.signals) == 1
    assert (
        result.signals[0].signal_type
        == "SERVICE_STOPPED"
    )


def test_stopped_required_service_produces_finding():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "display_name": "Print Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert len(result.findings) == 1
    assert (
        result.findings[0].finding_type
        == "SERVICE_UNAVAILABLE"
    )


def test_stopped_required_service_produces_recommendation():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "display_name": "Print Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert len(result.recommendations) == 1
    assert (
        result.recommendations[0]
        .recommendation_type
        == "REVIEW_SERVICE_STATE"
    )


def test_finding_preserves_signal_identity():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert (
        result.findings[0].supporting_signals[0]
        is result.signals[0]
    )


def test_disabled_required_service_is_detected():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "DISABLED",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert len(result.signals) == 1
    assert (
        result.signals[0].signal_type
        == "SERVICE_DISABLED"
    )

    assert (
        result.findings[0].finding_type
        == "SERVICE_DISABLED"
    )


def test_non_required_stopped_service_is_ignored():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "ExampleService",
                "status": "STOPPED",
                "start_type": "MANUAL",
                "required": False,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_multiple_services_are_processed():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "HealthyService",
                "status": "RUNNING",
                "start_type": "AUTO",
                "required": True,
            },
            {
                "name": "BrokenService",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            },
        ]
    )

    result = diagnostic.analyze(evidence)

    assert len(result.signals) == 1
    assert len(result.findings) == 1
    assert len(result.recommendations) == 1


def test_result_contains_no_authorization():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert not hasattr(
        result,
        "authorization",
    )

    assert not hasattr(
        result,
        "authorized",
    )


def test_result_contains_no_remediation_execution():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    result = diagnostic.analyze(evidence)

    assert not hasattr(
        result,
        "execution_status",
    )

    assert not hasattr(
        result,
        "remediation_result",
    )


def test_each_analysis_returns_fresh_result():
    diagnostic = WindowsServicesDiagnostic()

    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    first = diagnostic.analyze(evidence)
    second = diagnostic.analyze(evidence)

    assert first is not second
    assert first.signals is not second.signals
    assert first.findings is not second.findings
    assert (
        first.recommendations
        is not second.recommendations
    )