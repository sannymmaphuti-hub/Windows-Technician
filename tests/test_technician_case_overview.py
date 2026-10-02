import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_overview import (
    TechnicianCaseOverview,
)
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(
        DiagnosticCase()
    )
    workflow.start_investigation()
    return workflow


@pytest.fixture
def history(workflow):
    return TechnicianRecoveryCycleHistory(
        workflow
    )


@pytest.fixture
def overview(workflow, history):
    return TechnicianCaseOverview(
        workflow,
        history,
    )


def test_overview_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseOverview(
            None,
            None,
        )


def test_overview_requires_cycle_history(
    workflow,
):
    with pytest.raises(ValueError):
        TechnicianCaseOverview(
            workflow,
            None,
        )


def test_overview_exposes_case_id(
    workflow,
    overview,
):
    assert overview.case_id == workflow.case.case_id


def test_overview_exposes_workflow_id(
    workflow,
    overview,
):
    assert overview.workflow_id == workflow.workflow_id


def test_overview_exposes_workflow_state(
    overview,
):
    assert overview.workflow_state is WorkflowState.INVESTIGATING


def test_overview_exposes_cycle_count(
    overview,
):
    assert overview.cycle_count == 1


def test_overview_exposes_current_cycle(
    history,
    overview,
):
    assert overview.current_cycle is history.latest_cycle


def test_overview_exposes_current_cycle_number(
    overview,
):
    assert overview.current_cycle_number == 0


def test_overview_exposes_outcome(
    overview,
):
    assert overview.outcome == "ACTIVE"


def test_overview_exposes_recovery_status(
    overview,
):
    assert overview.is_recovery is False


def test_overview_updates_after_recovery_cycle(
    workflow,
    history,
    overview,
):
    cycle = history.latest_cycle.start_recovery_cycle()

    history.record_cycle(
        cycle
    )

    assert overview.cycle_count == 2
    assert overview.current_cycle_number == 1
    assert overview.current_cycle is cycle
    assert overview.is_recovery is True


def test_overview_is_read_only(
    overview,
):
    original_state = overview.workflow_state

    assert overview.workflow_state is original_state

    with pytest.raises(AttributeError):
        overview.workflow_state = WorkflowState.RESOLVED


def test_overview_does_not_change_workflow(
    workflow,
    history,
):
    original_state = workflow.state
    original_history = workflow.history

    TechnicianCaseOverview(
        workflow,
        history,
    )

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_overview_reflects_resolved_workflow(
    workflow,
    history,
):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    overview = TechnicianCaseOverview(
        workflow,
        history,
    )

    assert overview.workflow_state is WorkflowState.RESOLVED
    assert overview.outcome == "RESOLVED"


def test_overview_reflects_escalated_workflow(
    workflow,
    history,
):
    workflow.escalate()

    overview = TechnicianCaseOverview(
        workflow,
        history,
    )

    assert overview.workflow_state is WorkflowState.ESCALATED
    assert overview.outcome == "ESCALATED"