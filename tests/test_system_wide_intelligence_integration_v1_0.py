from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def test_integration_requires_diagnostic_case():
    try:
        SystemWideIntelligenceIntegration(None)
    except ValueError as exc:
        assert "DiagnosticCase" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_integration_uses_canonical_case():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    assert integration.case is case


def test_case_projection_preserves_canonical_case_identity():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    projection = integration.case_projection()

    assert projection["case_id"] == case.case_id
    assert set(projection) == {
        "case_id",
        "observations",
        "signals",
        "correlations",
        "findings",
        "root_causes",
        "recommendations",
    }


def test_case_projection_is_defensive():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    projection = integration.case_projection()

    projection["observations"].append("tampered")

    assert integration.case_projection()["observations"] == []


def test_intelligence_projection_has_canonical_domains():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    projection = integration.intelligence_projection()

    assert set(projection) == {
        "investigation",
        "relationships",
        "root_cause_reasoning",
        "recommendations",
    }


def test_full_projection_has_case_and_intelligence_surfaces():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    projection = integration.projection()

    assert set(projection) == {
        "case",
        "intelligence",
    }

    assert projection["case"]["case_id"] == case.case_id


def test_custom_components_can_be_composed():
    case = DiagnosticCase()

    investigation = {"domain": "investigation"}
    relationships = {"domain": "relationships"}
    reasoning = {"domain": "root_cause"}
    recommendations = {"domain": "recommendations"}

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=investigation,
        relationships=relationships,
        root_cause_reasoning=reasoning,
        recommendations=recommendations,
    )

    projection = integration.intelligence_projection()

    assert projection["investigation"] == investigation
    assert projection["relationships"] == relationships
    assert projection["root_cause_reasoning"] == reasoning
    assert projection["recommendations"] == recommendations


def test_custom_projection_objects_are_supported():
    class Projection:
        def projection(self):
            return {"value": "projection"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Projection(),
    )

    result = integration.intelligence_projection()

    assert result["investigation"] == {
        "value": "projection"
    }


def test_unknown_component_surface_is_safe():
    class Unknown:
        pass

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Unknown(),
    )

    result = integration.intelligence_projection()

    assert result["investigation"] == {}
