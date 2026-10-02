from datetime import datetime, timezone
from time import sleep

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(
    workflow,
    technician="Test Technician",
    reason="Issue resolved and verified.",
):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason=reason,
    )


def test_closure_has_creation_timestamp():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert isinstance(closure.created_at, datetime)


def test_closure_timestamp_is_timezone_aware():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.created_at.tzinfo is not None
    assert closure.created_at.utcoffset() is not None


def test_closure_timestamp_is_utc():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.created_at.tzinfo == timezone.utc


def test_closure_timestamp_is_not_in_the_future():
    workflow = build_workflow()
    resolve_workflow(workflow)

    before = datetime.now(timezone.utc)
    closure = build_closure(workflow)
    after = datetime.now(timezone.utc)

    assert before <= closure.created_at <= after


def test_closure_timestamp_is_created_after_resolution():
    workflow = build_workflow()

    resolve_workflow(workflow)
    resolution_time = datetime.now(timezone.utc)

    closure = build_closure(workflow)

    assert closure.created_at >= resolution_time


def test_closure_timestamp_is_stable():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    timestamp_before = closure.created_at

    workflow.reopen()

    assert closure.created_at == timestamp_before


def test_closure_timestamp_does_not_change_when_workflow_reopens():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)
    created_at = closure.created_at

    workflow.reopen()

    assert closure.created_at is created_at


def test_closure_timestamp_does_not_change_when_workflow_resolves_again():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)
    created_at = closure.created_at

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert closure.created_at is created_at


def test_two_closures_have_distinct_timestamps():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(workflow)

    sleep(0.001)

    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure record.",
    )

    assert first.created_at != second.created_at


def test_second_closure_has_later_timestamp_when_created_later():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(workflow)

    sleep(0.001)

    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure record.",
    )

    assert second.created_at > first.created_at


def test_closure_timestamp_is_independent_of_closure_id():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.created_at is not closure.closure_id


def test_closure_timestamp_is_independent_of_workflow_created_at():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.created_at != workflow.created_at


def test_closure_timestamp_belongs_to_closure_record():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    timestamp = closure.created_at

    assert timestamp == closure.created_at
    assert isinstance(timestamp, datetime)


def test_reopening_does_not_create_new_closure_timestamp():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)
    timestamp_before = closure.created_at

    workflow.reopen()

    timestamp_after = closure.created_at

    assert timestamp_after == timestamp_before


def test_new_closure_after_reopen_gets_new_timestamp():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(workflow)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    sleep(0.001)

    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Resolved after another recovery cycle.",
    )

    assert second.created_at > first.created_at


def test_closure_temporal_metadata_remains_stable_with_second_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First verified resolution.",
    )

    first_timestamp = first.created_at
    first_id = first.closure_id

    sleep(0.001)

    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second verified resolution.",
    )

    assert first.created_at == first_timestamp
    assert first.closure_id == first_id
    assert second.created_at > first.created_at