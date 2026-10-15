from pathlib import Path


ARCHITECTURE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "v1.0_architecture.md"
)


def test_v1_0_architecture_specification_exists():
    assert ARCHITECTURE.exists()


def test_v1_0_architecture_specification_is_not_empty():
    assert ARCHITECTURE.read_text(encoding="utf-8").strip()


def test_v1_0_architecture_documents_canonical_objects():
    text = ARCHITECTURE.read_text(encoding="utf-8")

    required = [
        "ManagedMachine",
        "RemoteSession",
        "DiagnosticCase",
        "TechnicianWorkflow",
        "Observation",
        "Signal",
        "Correlation",
        "Finding",
        "RootCause",
        "Explanation",
        "Recommendation",
        "RemediationOperation",
        "Verification",
        "Recovery",
    ]

    for name in required:
        assert name in text


def test_v1_0_architecture_documents_safety_boundary():
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "Eligibility" in text
    assert "Decision" in text
    assert "Authorization" in text
    assert "Execution" in text
    assert "Verification" in text


def test_v1_0_architecture_documents_canonical_intelligence_pipeline():
    text = ARCHITECTURE.read_text(encoding="utf-8")

    required = [
        "SystemWideIntelligence",
        "SystemLevelInvestigation",
        "SystemProblemRelationships",
        "SystemRootCauseReasoning",
        "SystemLevelRecommendations",
        "V1InvestigationPipeline",
    ]

    for name in required:
        assert name in text


def test_v1_0_architecture_prohibits_duplicate_fleet_intelligence():
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "Fleet is the canonical fleet boundary" in text
    assert "parallel FleetIntelligence" in text
