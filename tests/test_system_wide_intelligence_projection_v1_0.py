from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)
from engine.system_wide_intelligence_projection import (
    SystemWideIntelligenceProjection,
)


def test_projection_requires_canonical_integration():
    try:
        SystemWideIntelligenceProjection(None)
    except ValueError as exc:
        assert "SystemWideIntelligenceIntegration" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_projection_exposes_case():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    result = projection.case()

    assert result["case_id"] == case.case_id


def test_projection_exposes_all_intelligence_domains():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    result = projection.intelligence()

    assert set(result) == {
        "investigation",
        "relationships",
        "root_cause_reasoning",
        "recommendations",
    }


def test_projection_is_defensive():
    class Investigation:
        def projection(self):
            return {
                "findings": ["HIGH_MEMORY"]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    projection = SystemWideIntelligenceProjection(integration)

    result = projection.investigation()

    result["findings"].append("tampered")

    assert projection.investigation() == {
        "findings": ["HIGH_MEMORY"]
    }


def test_projection_returns_complete_surface():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    result = projection.projection()

    assert set(result) == {
        "case",
        "intelligence",
    }

    assert set(result["intelligence"]) == {
        "investigation",
        "relationships",
        "root_cause_reasoning",
        "recommendations",
    }


def test_projection_reflects_latest_integration_results():
    class Investigation:
        def investigate(self, system_data=None):
            return {
                "status": system_data["status"]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    integration.investigate({
        "status": "CURRENT"
    })

    projection = SystemWideIntelligenceProjection(integration)

    assert projection.investigation() == {
        "status": "CURRENT"
    }


def test_projection_does_not_own_intelligence_processing():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    forbidden = {
        "investigate",
        "analyze",
        "analyze_relationships",
        "analyze_root_causes",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(
        set(dir(projection))
    )
