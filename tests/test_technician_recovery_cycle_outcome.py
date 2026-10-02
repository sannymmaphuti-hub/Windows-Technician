import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def workflow():
    return TechnicianWorkflow(
        DiagnosticCase()
    )


def test_cycle_starts_active(workflow):
    workflow.start_investigation()

    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.outcome == "ACTIVE"


def test_cycle_is_active_while_investigating(workflow):
    workflow.start_investigation()

    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.outcome == "ACTIVE"


def test_cycle_is_resolved_when_workflow_resolves(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.outcome == "RESOLVED"


def test_cycle_is_escalated_when_workflow_escalates(workflow):
    workflow.start_investigation()
    workflow.escalate()

    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.outcome == "ESCALATED"


def test_outcome_is_read_only(workflow):
    workflow.start_investigation()

    cycle = TechnicianRecoveryCycle(workflow)

    with pytest.raises(AttributeError):
        cycle.outcome = "RESOLVED"


def test_cycle_outcome_updates_with_workflow(workflow):
    workflow.start_investigation()

    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.outcome == "ACTIVE"

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert cycle.outcome == "RESOLVED"


def test_recovery_cycle_can_become_escalated(workflow):
    workflow.start_investigation()

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    workflow.escalate()

    assert cycle.is_recovery is True
    assert cycle.outcome == "ESCALATED"


def test_original_cycle_remains_original(workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=0,
    )

    assert cycle.is_original is True
    assert cycle.is_recovery is False