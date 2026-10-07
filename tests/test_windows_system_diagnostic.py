from engine.windows_diagnostic_result import WindowsDiagnosticResult
from engine.windows_system_diagnostic import WindowsSystemDiagnostic
from engine.windows_system_evidence import WindowsSystemEvidence


def test_system_diagnostic_domain_is_system():
    diagnostic = WindowsSystemDiagnostic()

    assert diagnostic.domain == "SYSTEM"


def test_omitted_evidence_returns_empty_canonical_result():
    diagnostic = WindowsSystemDiagnostic()

    result = diagnostic.analyze()

    assert isinstance(result, WindowsDiagnosticResult)
    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.primary_cause is None
    assert result.recommendations == []
    assert result.confidences == []


def test_explicit_none_evidence_is_rejected():
    diagnostic = WindowsSystemDiagnostic()

    try:
        diagnostic.analyze(None)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Explicit None evidence must be rejected."
        )


def test_wrong_evidence_type_is_rejected():
    diagnostic = WindowsSystemDiagnostic()

    try:
        diagnostic.analyze({"operating_system": "Windows"})
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Wrong evidence type must be rejected."
        )


def test_healthy_system_produces_empty_canonical_result():
    diagnostic = WindowsSystemDiagnostic()

    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    result = diagnostic.analyze(evidence)

    assert isinstance(result, WindowsDiagnosticResult)
    assert result.observations == []
    assert result.signals == []
    assert result.findings == []
    assert result.correlations == []
    assert result.candidates == []
    assert result.primary_cause is None
    assert result.recommendations == []
    assert result.confidences == []


def test_missing_os_information_produces_canonical_result():
    diagnostic = WindowsSystemDiagnostic()

    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="",
        os_version="",
        architecture="",
        processor="AMD Ryzen",
    )

    result = diagnostic.analyze(evidence)

    assert isinstance(result, WindowsDiagnosticResult)

    assert len(result.signals) == 1
    assert len(result.findings) == 1
    assert len(result.recommendations) == 1

    assert (
        result.signals[0].signal_type
        == "SYSTEM_OS_INFORMATION_MISSING"
    )

    assert (
        result.findings[0].finding_type
        == "SYSTEM_OS_INFORMATION_MISSING"
    )

    assert (
        result.recommendations[0].recommendation_type
        == "REVIEW_SYSTEM_INFORMATION"
    )


def test_signal_identity_is_preserved_in_finding():
    diagnostic = WindowsSystemDiagnostic()

    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    result = diagnostic.analyze(evidence)

    assert result.signals[0] is (
        result.findings[0].supporting_signals[0]
    )