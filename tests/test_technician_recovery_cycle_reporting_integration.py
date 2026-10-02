import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_reopening import (
    TechnicianCaseReopening,
)
from engine.technician_case_reopening_lifecycle import (
    ReopeningState,
)
from engine.technician_recovery_cycle_reporting_integration import (
    TechnicianRecoveryCycleReportingIntegration,
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
def integration(workflow):
    return TechnicianRecoveryCycleReportingIntegration(
        workflow
    )


def test_integration_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianRecoveryCycleReportingIntegration(
            None
        )


def test_integration_exposes_workflow(
    workflow,
):
    integration = TechnicianRecoveryCycleReportingIntegration(
        workflow
    )

    assert integration.workflow is workflow


def test_integration_exposes_cycle_history(
    integration,
):
    assert integration.cycle_history is not None
    assert integration.cycle_history.cycle_count == 1


def test_integration_exposes_cycle_audit(
    integration,
):
    assert integration.cycle_audit is not None
    assert integration.cycle_audit.entries == []


def test_integration_exposes_cycle_report(
    integration,
):
    assert integration.cycle_report is not None
    assert integration.cycle_report.cycle_count == 1
    assert integration.cycle_report.current_cycle_number == 0


def test_record_cycle_updates_audit_and_report(
    workflow,
    integration,
):
    cycle = integration.cycle_history.latest_cycle.start_recovery_cycle()

    integration.cycle_history.record_cycle(
        cycle
    )

    integration.cycle_audit.record_cycle(
        cycle
    )

    assert integration.cycle_audit.entries[0][
        "cycle_number"
    ] == 1

    assert integration.cycle_report.cycle_count == 2
    assert integration.cycle_report.current_cycle_number == 1
    assert integration.cycle_report.is_recovery is True


def test_report_does_not_mutate_workflow(
    workflow,
    integration,
):
    original_state = workflow.state
    original_history = workflow.history

    _ = integration.cycle_report

    assert workflow.state is original_state
    assert workflow.history == original_history


def test_reporting_objects_share_workflow(
    workflow,
    integration,
):
    assert integration.cycle_history.workflow is workflow
    assert integration.cycle_audit.workflow is workflow
    assert integration.cycle_report.history is (
        integration.cycle_history
    )
    assert integration.cycle_report.audit is (
        integration.cycle_audit
    )


def test_reporting_integration_preserves_original_cycle(
    integration,
):
    cycle = integration.cycle_history.latest_cycle

    assert cycle.cycle_number == 0
    assert cycle.is_original is True
    assert cycle.is_recovery is False

    assert (
        integration.cycle_report.current_cycle
        is cycle
    )


def test_reporting_integration_rejects_cross_workflow_cycle(
    workflow,
    integration,
):
    other_workflow = TechnicianWorkflow(
        DiagnosticCase()
    )

    cycle = integration.cycle_history.latest_cycle.start_recovery_cycle()

    foreign_cycle = type(cycle)(
        other_workflow,
        cycle_number=cycle.cycle_number,
    )

    with pytest.raises(ValueError):
        integration.cycle_audit.record_cycle(
            foreign_cycle
        )


def test_reporting_integration_is_read_only_from_report(
    integration,
):
    cycles = integration.cycle_report.cycles

    cycles.clear()

    assert integration.cycle_report.cycle_count == 1