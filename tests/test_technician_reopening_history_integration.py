import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_case_timeline import TechnicianCaseTimeline
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def workflow():
    case = DiagnosticCase()
    return TechnicianWorkflow(case)


@pytest.fixture
def resolved_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager):
    return manager.request_reopening(
        "Technician A",
        "Issue returned after case closure.",
    )


def test_activity_log_records_reopening_request(
    manager,
    reopening,
):
    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    activity_log.record_reopening_request(
        reopening
    )

    entry = activity_log.entries[-1]

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "REQUESTED"
    assert entry["reopening"] is reopening


def test_activity_log_records_reopening_acceptance(
    manager,
    reopening,
):
    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    activity_log.record_reopening_status(
        lifecycle
    )

    entry = activity_log.entries[-1]

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "ACCEPTED"


def test_activity_log_records_reopening_rejection(
    manager,
    reopening,
):
    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.reject_reopening(lifecycle)

    activity_log.record_reopening_status(
        lifecycle
    )

    entry = activity_log.entries[-1]

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "REJECTED"


def test_activity_log_records_reopening_completion(
    manager,
    reopening,
):
    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)
    manager.complete_reopening(lifecycle)

    activity_log.record_reopening_status(
        lifecycle
    )

    entry = activity_log.entries[-1]

    assert entry["type"] == "REOPENING"
    assert entry["status"] == "COMPLETED"


def test_activity_log_preserves_reopening_order(
    manager,
    reopening,
):
    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    activity_log.record_reopening_request(
        reopening
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    activity_log.record_reopening_status(
        lifecycle
    )

    assert [
        entry["status"]
        for entry in activity_log.entries
        if entry["type"] == "REOPENING"
    ] == [
        "REQUESTED",
        "ACCEPTED",
    ]


def test_activity_log_rejects_invalid_reopening_request():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    activity_log = TechnicianActivityLog(
        workflow
    )

    with pytest.raises(ValueError):
        activity_log.record_reopening_request(
            object()
        )


def test_activity_log_rejects_foreign_reopening(
    manager,
):
    foreign_case = DiagnosticCase()
    foreign_workflow = TechnicianWorkflow(
        foreign_case
    )

    foreign_workflow.start_investigation()
    foreign_workflow.mark_diagnosed()
    foreign_workflow.require_action()
    foreign_workflow.start_remediation()
    foreign_workflow.start_verification()
    foreign_workflow.resolve()

    foreign_manager = TechnicianCaseReopeningManager(
        foreign_workflow
    )

    foreign_reopening = foreign_manager.request_reopening(
        "Technician B",
        "Foreign case reopening.",
    )

    activity_log = TechnicianActivityLog(
        manager.workflow
    )

    with pytest.raises(ValueError):
        activity_log.record_reopening_request(
            foreign_reopening
        )


def test_timeline_reflects_reopen_transition(
    manager,
    reopening,
):
    timeline = TechnicianCaseTimeline(
        manager.workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    assert timeline.events[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_summary_reflects_reopened_workflow(
    manager,
    reopening,
):
    summary = TechnicianCaseSummary(
        manager.workflow
    )

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    assert summary.workflow_state is (
        WorkflowState.INVESTIGATING
    )
    assert summary.is_terminal is False


def test_summary_preserves_case_identity_after_reopening(
    manager,
    reopening,
):
    summary = TechnicianCaseSummary(
        manager.workflow
    )

    original_case_id = summary.case_id
    original_workflow_id = summary.workflow_id

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    assert summary.case_id == original_case_id
    assert summary.workflow_id == original_workflow_id


def test_reopening_history_does_not_create_second_workflow(
    manager,
    reopening,
):
    timeline = TechnicianCaseTimeline(
        manager.workflow
    )

    summary = TechnicianCaseSummary(
        manager.workflow
    )

    original_workflow_id = manager.workflow.workflow_id

    lifecycle = manager.create_lifecycle(
        reopening
    )

    manager.accept_reopening(lifecycle)

    assert manager.workflow.workflow_id == (
        original_workflow_id
    )

    assert summary.workflow_id == (
        original_workflow_id
    )

    assert timeline.workflow.workflow_id == (
        original_workflow_id
    )