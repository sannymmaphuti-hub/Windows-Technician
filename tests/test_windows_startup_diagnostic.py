# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP DIAGNOSTIC TESTS
# ==========================================

from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_startup_diagnostic import (
    WindowsStartupDiagnostic,
)
from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


def test_diagnostic_has_startup_domain():
    diagnostic = WindowsStartupDiagnostic()

    assert diagnostic.domain == "STARTUP"


def test_omitted_evidence_returns_empty_result():
    diagnostic = WindowsStartupDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.primary_cause is None
    assert result.recommendations == []


def test_none_evidence_is_rejected():
    diagnostic = WindowsStartupDiagnostic()

    try:
        diagnostic.analyze(None)
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for None evidence."
    )


def test_invalid_evidence_is_rejected():
    diagnostic = WindowsStartupDiagnostic()

    try:
        diagnostic.analyze({})
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid evidence."
    )


def test_healthy_startup_produces_empty_result():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "OneDrive",
                "command": "OneDrive.exe",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_problematic_startup_produces_signal():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert len(result.signals) == 1

    signal = result.signals[0]

    assert signal.signal_type == (
        "STARTUP_COMMAND_MISSING"
    )
    assert signal.subject == "BrokenStartup"


def test_problematic_startup_produces_finding():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert len(result.findings) == 1

    finding = result.findings[0]

    assert finding.finding_type == (
        "STARTUP_COMMAND_MISSING"
    )
    assert finding.category == "STARTUP"
    assert finding.severity == "MEDIUM"


def test_finding_preserves_signal_identity():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert (
        result.findings[0].supporting_signals[0]
        is result.signals[0]
    )


def test_problematic_startup_produces_recommendation():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert len(result.recommendations) == 1

    recommendation = (
        result.recommendations[0]
    )

    assert recommendation.recommendation_type == (
        "REVIEW_STARTUP_ENTRY"
    )
    assert recommendation.category == "STARTUP"
    assert recommendation.priority == "MEDIUM"


def test_disabled_startup_item_is_not_reported():
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

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_multiple_startup_items_are_processed():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "Healthy",
                "command": "Healthy.exe",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
            {
                "name": "BrokenOne",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
            {
                "name": "BrokenTwo",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            },
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert len(result.signals) == 2
    assert len(result.findings) == 2
    assert len(result.recommendations) == 2


def test_diagnostic_does_not_create_remediation():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "BrokenStartup",
                "command": "",
                "location": "HKCU\\Run",
                "user": "User",
                "enabled": True,
            }
        ]
    )

    result = WindowsStartupDiagnostic().analyze(
        evidence
    )

    assert not hasattr(
        result,
        "remediation_actions",
    )