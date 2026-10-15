from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def test_relationship_analysis_is_not_run_during_construction():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    assert integration.relationship_result() is None


def test_analyze_relationships_uses_canonical_relationship_engine():
    class Relationships:
        def __init__(self):
            self.received = None

        def analyze(self, evidence):
            self.received = evidence
            return {
                "relationships": [
                    "memory_pressure -> process_load"
                ]
            }

    case = DiagnosticCase()
    relationships = Relationships()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=relationships,
    )

    evidence = {
        "findings": [
            "HIGH_MEMORY_USAGE",
            "HIGH_PROCESS_MEMORY",
        ]
    }

    result = integration.analyze_relationships(evidence)

    assert result == {
        "relationships": [
            "memory_pressure -> process_load"
        ]
    }
    assert relationships.received == evidence


def test_relationship_result_is_defensive():
    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": ["memory_pressure"]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=Relationships(),
    )

    result = integration.analyze_relationships({})

    result["relationships"].append("tampered")

    assert integration.relationship_result() == {
        "relationships": ["memory_pressure"]
    }


def test_relationship_result_is_available_in_projection():
    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": [
                    "process -> memory"
                ]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=Relationships(),
    )

    integration.analyze_relationships({"evidence": True})

    projection = integration.intelligence_projection()

    assert projection["relationships"] == {
        "relationships": [
            "process -> memory"
        ]
    }


def test_latest_relationship_analysis_replaces_previous_result():
    class Relationships:
        def analyze(self, evidence):
            return {
                "evidence": evidence
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=Relationships(),
    )

    integration.analyze_relationships({"run": 1})
    integration.analyze_relationships({"run": 2})

    assert integration.relationship_result() == {
        "evidence": {"run": 2}
    }


def test_relationship_analysis_does_not_replace_canonical_case():
    class Relationships:
        def analyze(self, evidence):
            return {"status": "ANALYZED"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=Relationships(),
    )

    integration.analyze_relationships({})

    assert integration.case is case
    assert integration.case.case_id == case.case_id


def test_projection_preserves_investigation_and_relationship_surfaces():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    class Relationships:
        def analyze(self, evidence):
            return {"status": "RELATED"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
        relationships=Relationships(),
    )

    integration.investigate({"system": True})
    integration.analyze_relationships({"evidence": True})

    projection = integration.projection()

    assert projection["intelligence"]["investigation"] == {
        "status": "INVESTIGATED"
    }

    assert projection["intelligence"]["relationships"] == {
        "status": "RELATED"
    }
