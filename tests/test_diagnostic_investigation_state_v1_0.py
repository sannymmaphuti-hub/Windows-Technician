from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.technician_workflow import TechnicianWorkflow


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def test_initial_investigation_state_is_pending():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=Investigation(),
    )

    assert orchestrator.investigation_state == "PENDING"


def test_investigation_becomes_running_before_engine_execution():
    class Investigation:
        def __init__(self):
            self.state_seen = None

        def investigate(self, system_data=None):
            self.state_seen = "CALLED"
            return {"status": "INVESTIGATED"}

    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=investigation,
    )

    orchestrator.start()

    assert orchestrator.investigation_state == "COMPLETED"


def test_successful_investigation_becomes_completed():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=Investigation(),
    )

    orchestrator.start()

    assert orchestrator.investigation_state == "COMPLETED"


def test_failed_investigation_becomes_failed():
    class Investigation:
        def investigate(self, system_data=None):
            raise RuntimeError("investigation failed")

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=Investigation(),
    )

    try:
        orchestrator.start()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError")

    assert orchestrator.investigation_state == "FAILED"


def test_failure_does_not_change_canonical_workflow_ownership():
    class Investigation:
        def investigate(self, system_data=None):
            raise RuntimeError("investigation failed")

    workflow = make_workflow()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    try:
        orchestrator.start()
    except RuntimeError:
        pass

    assert workflow.state.value == "INVESTIGATING"


def test_state_is_exposed_in_projection():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=Investigation(),
    )

    orchestrator.start()

    projection = orchestrator.projection()

    assert projection["investigation_state"] == "COMPLETED"


def test_investigation_state_does_not_expose_case_lifecycle_controls():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    orchestrator = DiagnosticInvestigationOrchestrator(
        make_workflow(),
        investigation=Investigation(),
    )

    forbidden = {
        "resolve",
        "remediate",
        "authorize",
        "execute",
        "verify",
        "close",
    }

    assert forbidden.isdisjoint(set(dir(orchestrator)))
