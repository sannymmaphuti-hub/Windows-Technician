import pytest

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


def test_closure_has_unique_identity():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(workflow)

    assert first.closure_id != second.closure_id


def test_closure_identity_is_string():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert isinstance(closure.closure_id, str)
    assert closure.closure_id.strip()


def test_closure_keeps_workflow_reference():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.workflow is workflow


def test_closure_keeps_workflow_identity():
    workflow = build_workflow()
    resolve_workflow(workflow)

    workflow_id_before = workflow.workflow_id
    closure = build_closure(workflow)

    assert closure.workflow.workflow_id == workflow_id_before


def test_closure_stores_technician():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(
        workflow,
        technician="Sanny Technician",
    )

    assert closure.technician == "Sanny Technician"


def test_closure_stores_reason():
    workflow = build_workflow()
    resolve_workflow(workflow)

    reason = "Memory pressure was resolved and the system was verified."
    closure = build_closure(
        workflow,
        reason=reason,
    )

    assert closure.reason == reason


def test_closure_captures_resolved_workflow_state():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.workflow_state.value == "RESOLVED"


def test_closure_state_matches_workflow_at_creation():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    assert closure.workflow_state is workflow.state


def test_closure_creation_does_not_change_workflow_state():
    workflow = build_workflow()
    resolve_workflow(workflow)

    state_before = workflow.state

    build_closure(workflow)

    assert workflow.state is state_before


def test_closure_creation_does_not_change_workflow_history():
    workflow = build_workflow()
    resolve_workflow(workflow)

    history_before = list(workflow.history)

    build_closure(workflow)

    assert workflow.history == history_before


def test_closure_remains_resolved_after_reopen():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    workflow.reopen()

    assert workflow.state.value == "INVESTIGATING"
    assert closure.workflow_state.value == "RESOLVED"


def test_closure_workflow_reference_tracks_same_workflow_after_reopen():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    workflow.reopen()

    assert closure.workflow is workflow
    assert closure.workflow.state.value == "INVESTIGATING"


def test_closure_metadata_survives_reopen():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(
        workflow,
        technician="Primary Technician",
        reason="Problem resolved after remediation.",
    )

    closure_id_before = closure.closure_id
    technician_before = closure.technician
    reason_before = closure.reason
    state_before = closure.workflow_state

    workflow.reopen()

    assert closure.closure_id == closure_id_before
    assert closure.technician == technician_before
    assert closure.reason == reason_before
    assert closure.workflow_state is state_before


def test_two_closures_have_independent_metadata():
    workflow = build_workflow()
    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First verified resolution.",
    )
    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure record.",
    )

    assert first.closure_id != second.closure_id
    assert first.technician != second.technician
    assert first.reason != second.reason
    assert first.workflow is second.workflow


def test_closure_does_not_alias_workflow_state_as_mutable_record():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_closure(workflow)

    workflow.reopen()

    assert closure.workflow_state.value == "RESOLVED"
    assert workflow.state.value == "INVESTIGATING"


def test_closure_requires_nonempty_technician():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="   ",
            reason="Issue resolved.",
        )


def test_closure_requires_nonempty_reason():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="Test Technician",
            reason="   ",
        )