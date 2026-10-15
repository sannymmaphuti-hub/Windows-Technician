from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def test_recommendation_generation_is_not_run_during_construction():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    assert integration.recommendation_result() is None


def test_generate_recommendations_uses_canonical_engine():
    class Recommendations:
        def __init__(self):
            self.received = None

        def generate(self, system_data=None):
            self.received = system_data
            return {
                "recommendations": [
                    "REDUCE_RESOURCE_PRESSURE"
                ]
            }

    case = DiagnosticCase()
    recommendations = Recommendations()

    integration = SystemWideIntelligenceIntegration(
        case,
        recommendations=recommendations,
    )

    system_data = {
        "memory_usage": 91,
        "process_count": 42,
    }

    result = integration.generate_recommendations(system_data)

    assert result == {
        "recommendations": [
            "REDUCE_RESOURCE_PRESSURE"
        ]
    }

    assert recommendations.received == system_data


def test_recommendation_result_is_defensive():
    class Recommendations:
        def generate(self, system_data=None):
            return {
                "recommendations": [
                    "REVIEW_MEMORY_USAGE"
                ]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        recommendations=Recommendations(),
    )

    result = integration.generate_recommendations()

    result["recommendations"].append("tampered")

    assert integration.recommendation_result() == {
        "recommendations": [
            "REVIEW_MEMORY_USAGE"
        ]
    }


def test_latest_recommendation_generation_replaces_previous_result():
    class Recommendations:
        def generate(self, system_data=None):
            return {
                "system_data": system_data
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        recommendations=Recommendations(),
    )

    integration.generate_recommendations({"run": 1})
    integration.generate_recommendations({"run": 2})

    assert integration.recommendation_result() == {
        "system_data": {"run": 2}
    }


def test_recommendation_result_is_projected():
    class Recommendations:
        def generate(self, system_data=None):
            return {
                "recommendation": "REVIEW_SYSTEM_LOAD"
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        recommendations=Recommendations(),
    )

    integration.generate_recommendations()

    projection = integration.intelligence_projection()

    assert projection["recommendations"] == {
        "recommendation": "REVIEW_SYSTEM_LOAD"
    }


def test_recommendation_generation_preserves_canonical_case():
    class Recommendations:
        def generate(self, system_data=None):
            return {
                "status": "GENERATED"
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        recommendations=Recommendations(),
    )

    integration.generate_recommendations()

    assert integration.case is case
    assert integration.case.case_id == case.case_id


def test_full_intelligence_surface_contains_all_four_domains():
    class Investigation:
        def investigate(self, system_data=None):
            return {"investigation": "complete"}

    class Relationships:
        def analyze(self, evidence):
            return {"relationships": "complete"}

    class Reasoning:
        def analyze(self, relationships):
            return {"root_cause": "complete"}

    class Recommendations:
        def generate(self, system_data=None):
            return {"recommendations": "complete"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
        relationships=Relationships(),
        root_cause_reasoning=Reasoning(),
        recommendations=Recommendations(),
    )

    integration.investigate({"system": True})
    integration.analyze_relationships(
        integration.investigation_result()
    )
    integration.analyze_root_causes()
    integration.generate_recommendations(
        integration.investigation_result()
    )

    intelligence = integration.intelligence_projection()

    assert intelligence == {
        "investigation": {
            "investigation": "complete"
        },
        "relationships": {
            "relationships": "complete"
        },
        "root_cause_reasoning": {
            "root_cause": "complete"
        },
        "recommendations": {
            "recommendations": "complete"
        },
    }
