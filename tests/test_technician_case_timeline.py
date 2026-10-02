import pytest

from engine.technician_case_timeline import TechnicianCaseTimeline
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


@pytest.fixture
def workflow():
    return TechnicianWorkflow(FakeCase())


@pytest.fixture
def timeline(workflow):
    return TechnicianCaseTimeline(workflow)


def test_timeline_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianCaseTimeline(None)


def test_timeline_exposes_workflow(
    timeline,
    workflow,
):
    assert timeline.workflow is workflow


def test_timeline_starts_empty(
    timeline,
):
    assert timeline.events == []


def test_timeline_reflects_workflow_history(
    timeline,
    workflow,
):
    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert timeline.events == [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        ),
        (
            WorkflowState.INVESTIGATING,
            WorkflowState.DIAGNOSED,
        ),
    ]


def test_timeline_preserves_event_order(
    timeline,
    workflow,
):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert timeline.events[0] == (
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
    )

    assert timeline.events[1] == (
        WorkflowState.INVESTIGATING,
        WorkflowState.DIAGNOSED,
    )

    assert timeline.events[2] == (
        WorkflowState.DIAGNOSED,
        WorkflowState.ACTION_REQUIRED,
    )


def test_timeline_updates_when_workflow_changes(
    timeline,
    workflow,
):
    assert timeline.events == []

    workflow.start_investigation()

    assert timeline.events == [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        )
    ]


def test_timeline_events_are_read_only(
    timeline,
    workflow,
):
    workflow.start_investigation()

    events = timeline.events
    events.clear()

    assert timeline.events == [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        )
    ]


def test_timeline_does_not_mutate_workflow(
    timeline,
    workflow,
):
    workflow.start_investigation()
    original_history = workflow.history

    _ = timeline.events

    assert workflow.history == original_history


def test_timeline_contains_all_workflow_transitions(
    timeline,
    workflow,
):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.escalate()

    assert timeline.events == workflow.history


def test_timeline_reflects_terminal_escalation(
    timeline,
    workflow,
):
    workflow.escalate()

    assert timeline.events == [
        (
            WorkflowState.OPEN,
            WorkflowState.ESCALATED,
        )
    ]


def test_timeline_reflects_resolution(
    timeline,
    workflow,
):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert timeline.events[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
    )


def test_timeline_is_live_projection(
    timeline,
    workflow,
):
    workflow.start_investigation()

    first_view = timeline.events

    workflow.mark_diagnosed()

    second_view = timeline.events

    assert first_view != second_view
    assert second_view == workflow.history