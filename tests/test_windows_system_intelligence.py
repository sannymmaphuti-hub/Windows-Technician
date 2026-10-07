from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)
from engine.windows_system_intelligence import (
    WindowsSystemIntelligence,
)


def test_healthy_system_produces_no_findings():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert isinstance(result, dict)
    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_missing_operating_system_creates_finding():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1

    signal = result["signals"][0]
    finding = result["findings"][0]
    recommendation = result["recommendations"][0]

    assert signal.signal_type == "SYSTEM_OS_INFORMATION_MISSING"
    assert signal.source == "SYSTEM"

    assert finding.finding_type == "SYSTEM_OS_INFORMATION_MISSING"
    assert finding.category == "SYSTEM"
    assert finding.severity == "MEDIUM"

    assert (
        recommendation.recommendation_type
        == "REVIEW_SYSTEM_INFORMATION"
    )
    assert recommendation.category == "SYSTEM"


def test_missing_os_version_creates_finding():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1

    assert (
        result["signals"][0].signal_type
        == "SYSTEM_OS_INFORMATION_MISSING"
    )


def test_missing_architecture_creates_finding():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="",
        processor="AMD Ryzen",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1


def test_missing_processor_does_not_create_system_problem():
    evidence = WindowsSystemEvidence(
        computer_name="TEST-PC",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_missing_computer_name_does_not_create_system_problem():
    evidence = WindowsSystemEvidence(
        computer_name="",
        operating_system="Windows",
        os_version="10.0.26200",
        architecture="AMD64",
        processor="AMD Ryzen",
    )

    intelligence = WindowsSystemIntelligence()

    result = intelligence.analyze(evidence)

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_invalid_evidence_is_rejected():
    intelligence = WindowsSystemIntelligence()

    try:
        intelligence.analyze(None)
    except ValueError:
        return

    raise AssertionError(
        "SYSTEM intelligence should reject invalid evidence."
    )