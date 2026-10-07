# ==========================================
# Windows Technician v0.9
# STORAGE DIAGNOSTIC INTELLIGENCE
# INTEGRATION TESTS
# ==========================================

from engine.signal import Signal
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_storage_diagnostic import (
    WindowsStorageDiagnostic,
)
from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)


def make_evidence(*volumes):
    return WindowsStorageEvidence(
        volumes=list(volumes)
    )


# ==========================================
# CONSTRUCTION
# ==========================================


def test_storage_diagnostic_can_be_created():
    diagnostic = WindowsStorageDiagnostic()

    assert diagnostic is not None


def test_storage_diagnostic_has_storage_domain():
    diagnostic = WindowsStorageDiagnostic()

    assert diagnostic.domain == "STORAGE"


# ==========================================
# NORMAL STORAGE
# ==========================================


def test_normal_storage_returns_canonical_result():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 500_000,
            }
        )
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )


def test_normal_storage_has_no_findings():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 500_000,
            }
        )
    )

    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.recommendations == []


# ==========================================
# STORAGE PRESSURE
# ==========================================


def test_low_free_space_produces_canonical_signal():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            }
        )
    )

    assert len(result.signals) == 1
    assert isinstance(
        result.signals[0],
        Signal,
    )

    assert (
        result.signals[0].signal_type
        == "LOW_FREE_SPACE"
    )


def test_low_free_space_produces_canonical_finding():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            }
        )
    )

    assert len(result.findings) == 1
    assert isinstance(
        result.findings[0],
        Finding,
    )

    assert (
        result.findings[0].finding_type
        == "STORAGE_PRESSURE"
    )


def test_low_free_space_produces_canonical_recommendation():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            }
        )
    )

    assert len(result.recommendations) == 1
    assert isinstance(
        result.recommendations[0],
        Recommendation,
    )

    assert (
        result.recommendations[0].recommendation_type
        == "REVIEW_STORAGE_USAGE"
    )


# ==========================================
# INTELLIGENCE RELATIONSHIPS
# ==========================================


def test_finding_supports_canonical_signal():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            }
        )
    )

    finding = result.findings[0]
    signal = result.signals[0]

    assert finding.supporting_signals[0] is signal


def test_result_preserves_storage_intelligence_objects():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert result.findings[0].severity == "CRITICAL"
    assert result.recommendations[0].priority == "CRITICAL"


# ==========================================
# MULTIPLE VOLUMES
# ==========================================


def test_multiple_problem_volumes_are_preserved():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 50_000,
            },
            {
                "drive": "D:\\",
                "total_bytes": 2_000_000,
                "free_bytes": 100_000,
            },
        )
    )

    assert len(result.signals) == 2
    assert len(result.findings) == 2
    assert len(result.recommendations) == 2

    assert result.signals[0].subject == "C:\\"
    assert result.signals[1].subject == "D:\\"


def test_healthy_and_problem_volumes_are_separated():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 500_000,
            },
            {
                "drive": "D:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            },
        )
    )

    assert len(result.signals) == 1
    assert len(result.findings) == 1
    assert len(result.recommendations) == 1

    assert result.signals[0].subject == "D:\\"


# ==========================================
# EMPTY / INVALID EVIDENCE
# ==========================================


def test_empty_storage_evidence_returns_empty_result():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        WindowsStorageEvidence()
    )

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


def test_invalid_storage_evidence_produces_no_intelligence():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 0,
                "free_bytes": 0,
            }
        )
    )

    assert result.signals == []
    assert result.findings == []
    assert result.recommendations == []


# ==========================================
# INPUT SAFETY
# ==========================================


def test_none_evidence_is_rejected():
    diagnostic = WindowsStorageDiagnostic()

    try:
        diagnostic.analyze(None)
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for None evidence."
    )


# ==========================================
# RESULT ISOLATION
# ==========================================


def test_each_diagnostic_run_returns_fresh_result():
    diagnostic = WindowsStorageDiagnostic()

    evidence = make_evidence(
        {
            "drive": "C:\\",
            "total_bytes": 1_000_000,
            "free_bytes": 100_000,
        }
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


# ==========================================
# DIAGNOSTIC BOUNDARIES
# ==========================================


def test_storage_diagnostic_does_not_authorize_remediation():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert not hasattr(
        result,
        "authorization",
    )

    assert not hasattr(
        result,
        "authorized",
    )


def test_storage_diagnostic_does_not_execute_remediation():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert not hasattr(
        result,
        "execution_status",
    )

    assert not hasattr(
        result,
        "remediation_result",
    )


def test_storage_diagnostic_does_not_create_case():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 30_000,
            }
        )
    )

    assert not hasattr(
        result,
        "case_id",
    )

    assert not hasattr(
        result,
        "lifecycle_state",
    )


# ==========================================
# RESULT CONTRACT
# ==========================================


def test_storage_diagnostic_result_has_canonical_fields():
    diagnostic = WindowsStorageDiagnostic()

    result = diagnostic.analyze(
        make_evidence(
            {
                "drive": "C:\\",
                "total_bytes": 1_000_000,
                "free_bytes": 100_000,
            }
        )
    )

    assert hasattr(result, "observations")
    assert hasattr(result, "signals")
    assert hasattr(result, "findings")
    assert hasattr(result, "correlations")
    assert hasattr(result, "candidates")
    assert hasattr(result, "primary_cause")
    assert hasattr(result, "recommendations")
    assert hasattr(result, "confidences")