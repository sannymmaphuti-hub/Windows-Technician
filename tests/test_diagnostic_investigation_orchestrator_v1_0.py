from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.technician_workflow import TechnicianWorkflow


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def test_orchestrator_requires_technician_workflow():
    try:
        DiagnosticInvestigationOrchestrator(None)
    except ValueError as exc:
        assert "TechnicianWorkflow" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_orchestrator_uses_canonical_case():
    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(workflow)

    assert orchestrator.case is workflow.case


def test_investigation_is_not_run_during_construction():
    class Investigation:
        def __init__(self):
            self.called = False

        def investigate(self, system_data=None):
            self.called = True
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()
    investigation = Investigation()

    DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    assert investigation.called is False


def test_start_enters_investigation_workflow_state():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    assert workflow.state.value == "INVESTIGATING"


def test_start_uses_canonical_investigation_engine():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {
                "status": "INVESTIGATED",
                "scope": "SYSTEM",
            }

    workflow = make_workflow()
    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    system_data = {
        "memory": 90,
        "cpu": 80,
    }

    result = orchestrator.start(system_data)

    assert investigation.received == system_data
    assert result == {
        "status": "INVESTIGATED",
        "scope": "SYSTEM",
    }


def test_result_is_defensive():
    class Investigation:
        def investigate(self, system_data=None):
            return {
                "findings": ["HIGH_MEMORY"]
            }

    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    result = orchestrator.start()

    result["findings"].append("tampered")

    assert orchestrator.result == {
        "findings": ["HIGH_MEMORY"]
    }


def test_projection_contains_case_workflow_and_investigation():
    class Investigation:
        def investigate(self, system_data=None):
            return {
                "status": "INVESTIGATED"
            }

    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    projection = orchestrator.projection()

    assert projection["case"]["case_id"] == workflow.case.case_id
    assert projection["workflow"]["state"].value == "INVESTIGATING"
    assert projection["investigation"] == {
        "status": "INVESTIGATED"
    }


def test_orchestrator_does_not_expose_remediation_processing():
    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(workflow)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "generate_recommendations",
        "analyze_root_causes",
    }

    assert forbidden.isdisjoint(set(dir(orchestrator)))
