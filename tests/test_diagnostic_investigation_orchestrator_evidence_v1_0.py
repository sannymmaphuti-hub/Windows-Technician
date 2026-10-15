from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.technician_workflow import TechnicianWorkflow


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def test_investigation_receives_case_evidence():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()

    workflow.case.observations = [{"type": "MEMORY", "value": 90}]
    workflow.case.signals = [{"type": "MEMORY_PRESSURE", "severity": "HIGH"}]
    workflow.case.correlations = [{"type": "MEMORY_CORRELATION"}]
    workflow.case.findings = [{"type": "HIGH_MEMORY"}]

    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    orchestrator.start()

    assert investigation.received == {
        "observations": [{"type": "MEMORY", "value": 90}],
        "signals": [{"type": "MEMORY_PRESSURE", "severity": "HIGH"}],
        "correlations": [{"type": "MEMORY_CORRELATION"}],
        "findings": [{"type": "HIGH_MEMORY"}],
    }


def test_explicit_system_data_remains_supported():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()
    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    explicit_data = {
        "cpu": 85,
        "memory": 92,
    }

    orchestrator.start(explicit_data)

    assert investigation.received == explicit_data


def test_case_evidence_is_defensive():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()
    workflow.case.observations = [{"type": "CPU", "value": 95}]

    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    orchestrator.start()

    investigation.received["observations"].append(
        {"type": "TAMPERED"}
    )

    assert workflow.case.observations == [
        {"type": "CPU", "value": 95}
    ]


def test_empty_case_evidence_is_supported():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {"status": "INVESTIGATED"}

    workflow = make_workflow()
    investigation = Investigation()

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=investigation,
    )

    orchestrator.start()

    assert investigation.received == {
        "observations": [],
        "signals": [],
        "correlations": [],
        "findings": [],
    }
