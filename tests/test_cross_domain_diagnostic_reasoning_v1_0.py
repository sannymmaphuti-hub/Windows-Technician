from engine.cross_domain_diagnostic_reasoning import (
    CrossDomainDiagnosticReasoning,
)
from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.technician_workflow import TechnicianWorkflow


def make_orchestrator():
    workflow = TechnicianWorkflow(DiagnosticCase())

    class Investigation:
        def investigate(self, system_data=None):
            return {
                "domains": {
                    "memory": {
                        "severity": "HIGH",
                    },
                    "process": {
                        "severity": "HIGH",
                    },
                },
                "evidence": [
                    "memory_pressure",
                    "high_process_usage",
                ],
            }

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    return orchestrator


def test_requires_canonical_orchestrator():
    try:
        CrossDomainDiagnosticReasoning(None)
    except ValueError as exc:
        assert "DiagnosticInvestigationOrchestrator" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_uses_existing_relationship_engine():
    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": [
                    {
                        "domains": ["memory", "process"],
                        "type": "RESOURCE_CONTENTION",
                    }
                ]
            }

    reasoning = CrossDomainDiagnosticReasoning(
        make_orchestrator(),
        relationships=Relationships(),
    )

    result = reasoning.analyze()

    assert result == {
        "relationships": [
            {
                "domains": ["memory", "process"],
                "type": "RESOURCE_CONTENTION",
            }
        ]
    }


def test_relationship_engine_receives_investigation_result():
    class Relationships:
        def __init__(self):
            self.received = None

        def analyze(self, evidence):
            self.received = evidence
            return {"status": "ANALYZED"}

    orchestrator = make_orchestrator()
    relationships = Relationships()

    reasoning = CrossDomainDiagnosticReasoning(
        orchestrator,
        relationships=relationships,
    )

    reasoning.analyze()

    assert relationships.received == orchestrator.result


def test_result_is_defensive():
    class Relationships:
        def analyze(self, evidence):
            return {
                "relationships": [
                    {"type": "RESOURCE_CONTENTION"}
                ]
            }

    reasoning = CrossDomainDiagnosticReasoning(
        make_orchestrator(),
        relationships=Relationships(),
    )

    result = reasoning.analyze()
    result["relationships"].append({"type": "TAMPERED"})

    assert reasoning.result == {
        "relationships": [
            {"type": "RESOURCE_CONTENTION"}
        ]
    }


def test_projection_contains_case_identity():
    class Relationships:
        def analyze(self, evidence):
            return {"status": "ANALYZED"}

    orchestrator = make_orchestrator()

    reasoning = CrossDomainDiagnosticReasoning(
        orchestrator,
        relationships=Relationships(),
    )

    reasoning.analyze()

    projection = reasoning.projection()

    assert projection["case_id"] == orchestrator.case.case_id
    assert projection["relationships"] == {
        "status": "ANALYZED"
    }


def test_does_not_expose_remediation_processing():
    reasoning = CrossDomainDiagnosticReasoning(
        make_orchestrator()
    )

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(reasoning)))
