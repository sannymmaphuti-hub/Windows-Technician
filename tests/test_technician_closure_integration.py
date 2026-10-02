import pytest

from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workflow import TechnicianWorkflow


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def resolved_workflow():
    workflow = TechnicianWorkflow(FakeCase())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def closure(resolved_workflow):
    return TechnicianCaseClosure(
        resolved_workflow,
        "tech-001",
        "Issue resolved and verified.",
    )


@pytest.fixture
def summary(resolved_workflow):
    return TechnicianCaseSummary(resolved_workflow)


@pytest.fixture
def activity_log(resolved_workflow):
    return TechnicianActivityLog(resolved_workflow)


def test_closure_can_be_attached_to_case_summary(
    summary,
    closure,
):
    summary.set_closure(closure)

    assert summary.closure is closure


def test_summary_exposes_closure_identity(
    summary,
    closure,
):
    summary.set_closure(closure)

    assert summary.closure_id == closure.closure_id


def test_summary_exposes_closure_technician(
    summary,
    closure,
):
    summary.set_closure(closure)

    assert summary.closure_technician == "tech-001"


def test_summary_exposes_closure_reason(
    summary,
    closure,
):
    summary.set_closure(closure)

    assert (
        summary.closure_reason
        == "Issue resolved and verified."
    )


def test_summary_exposes_closure_state(
    summary,
    closure,
):
    summary.set_closure(closure)

    assert summary.closure_state == closure.workflow_state


def test_closure_can_be_recorded_in_activity_log(
    activity_log,
    closure,
):
    activity_log.record_closure(closure)

    entries = activity_log.entries

    assert len(entries) == 1
    assert entries[0]["type"] == "CLOSURE"
    assert entries[0]["closure"] is closure


def test_activity_log_preserves_closure_record(
    activity_log,
    closure,
):
    activity_log.record_closure(closure)

    assert activity_log.entries[0]["closure"].closure_id == (
        closure.closure_id
    )


def test_closure_integration_does_not_change_workflow(
    summary,
    activity_log,
    closure,
    resolved_workflow,
):
    original_state = resolved_workflow.state
    original_history = resolved_workflow.history

    summary.set_closure(closure)
    activity_log.record_closure(closure)

    assert resolved_workflow.state is original_state
    assert resolved_workflow.history == original_history