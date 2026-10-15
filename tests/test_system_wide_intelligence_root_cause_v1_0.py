from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def test_root_cause_reasoning_is_not_run_during_construction():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    assert integration.root_cause_result() is None


def test_analyze_root_causes_uses_canonical_reasoning_engine():
    class Reasoning:
        def __init__(self):
            self.received = None

        def analyze(self, relationships):
            self.received = relationships
            return {
                "root_causes": [
                    "RESOURCE_CONTENTION"
                ]
            }

    case = DiagnosticCase()
    reasoning = Reasoning()

    integration = SystemWideIntelligenceIntegration(
        case,
        root_cause_reasoning=reasoning,
    )

    relationships = {
        "relationships": [
            "memory_pressure -> process_load"
        ]
    }

    result = integration.analyze_root_causes(relationships)

    assert result == {
        "root_causes": [
            "RESOURCE_CONTENTION"
        ]
    }
    assert reasoning.received == relationships


def test_root_cause_analysis_defaults_to_latest_relationship_result():
    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": [
                    "memory -> process"
                ]
            }

    class Reasoning:
        def __init__(self):
            self.received = None

        def analyze(self, relationships):
            self.received = relationships
            return {
                "root_cause": "RESOURCE_CONTENTION"
            }

    case = DiagnosticCase()
    reasoning = Reasoning()

    integration = SystemWideIntelligenceIntegration(
        case,
        relationships=Relationships(),
        root_cause_reasoning=reasoning,
    )

    integration.analyze_relationships({"evidence": True})
    result = integration.analyze_root_causes()

    assert reasoning.received == {
        "relationships": [
            "memory -> process"
        ]
    }

    assert result == {
        "root_cause": "RESOURCE_CONTENTION"
    }


def test_root_cause_result_is_defensive():
    class Reasoning:
        def analyze(self, relationships):
            return {
                "root_causes": ["RESOURCE_CONTENTION"]
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        root_cause_reasoning=Reasoning(),
    )

    result = integration.analyze_root_causes({})

    result["root_causes"].append("tampered")

    assert integration.root_cause_result() == {
        "root_causes": ["RESOURCE_CONTENTION"]
    }


def test_latest_root_cause_analysis_replaces_previous_result():
    class Reasoning:
        def analyze(self, relationships):
            return {
                "relationships": relationships
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        root_cause_reasoning=Reasoning(),
    )

    integration.analyze_root_causes({"run": 1})
    integration.analyze_root_causes({"run": 2})

    assert integration.root_cause_result() == {
        "relationships": {"run": 2}
    }


def test_root_cause_result_is_projected():
    class Reasoning:
        def analyze(self, relationships):
            return {
                "root_cause": "RESOURCE_CONTENTION"
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        root_cause_reasoning=Reasoning(),
    )

    integration.analyze_root_causes({})

    projection = integration.intelligence_projection()

    assert projection["root_cause_reasoning"] == {
        "root_cause": "RESOURCE_CONTENTION"
    }


def test_full_system_intelligence_chain_can_be_composed():
    class Investigation:
        def investigate(self, system_data=None):
            return {
                "findings": ["HIGH_MEMORY"]
            }

    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": ["memory -> process"]
            }

    class Reasoning:
        def analyze(self, relationships):
            return {
                "root_cause": "RESOURCE_CONTENTION"
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
        relationships=Relationships(),
        root_cause_reasoning=Reasoning(),
    )

    integration.investigate({"memory": 90})
    integration.analyze_relationships(
        integration.investigation_result()
    )
    integration.analyze_root_causes()

    projection = integration.projection()

    assert projection["intelligence"]["investigation"] == {
        "findings": ["HIGH_MEMORY"]
    }

    assert projection["intelligence"]["relationships"] == {
        "relationships": ["memory -> process"]
    }

    assert projection["intelligence"]["root_cause_reasoning"] == {
        "root_cause": "RESOURCE_CONTENTION"
    }
