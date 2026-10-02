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


def build_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )


def build_resolved_closure():
    workflow = build_workflow()
    resolve_workflow(workflow)
    return workflow, build_closure(workflow)


def test_closure_id_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.closure_id

    with pytest.raises(AttributeError):
        closure.closure_id = "replacement"

    assert closure.closure_id == original


def test_created_at_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.created_at

    with pytest.raises(AttributeError):
        closure.created_at = original

    assert closure.created_at is original


def test_technician_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.technician

    with pytest.raises(AttributeError):
        closure.technician = "Another Technician"

    assert closure.technician == original


def test_reason_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.reason

    with pytest.raises(AttributeError):
        closure.reason = "Changed reason"

    assert closure.reason == original


def test_workflow_state_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.workflow_state

    with pytest.raises(AttributeError):
        closure.workflow_state = workflow.state

    assert closure.workflow_state is original


def test_case_id_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.case_id

    with pytest.raises(AttributeError):
        closure.case_id = "replacement-case"

    assert closure.case_id == original


def test_workflow_id_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.workflow_id

    with pytest.raises(AttributeError):
        closure.workflow_id = "replacement-workflow"

    assert closure.workflow_id == original


def test_workflow_reference_is_read_only():
    workflow, closure = build_resolved_closure()
    original = closure.workflow

    with pytest.raises(AttributeError):
        closure.workflow = TechnicianWorkflow(DiagnosticCase())

    assert closure.workflow is original


def test_failed_id_mutation_does_not_change_metadata():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.case_id,
        closure.workflow_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.created_at,
    )

    with pytest.raises(AttributeError):
        closure.closure_id = "replacement"

    assert (
        closure.closure_id,
        closure.case_id,
        closure.workflow_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.created_at,
    ) == original


def test_failed_technician_mutation_does_not_change_metadata():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    )

    with pytest.raises(AttributeError):
        closure.technician = "Replacement Technician"

    assert (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    ) == original


def test_failed_reason_mutation_does_not_change_metadata():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    )

    with pytest.raises(AttributeError):
        closure.reason = "Replacement reason"

    assert (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    ) == original


def test_failed_state_mutation_does_not_change_metadata():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    )

    with pytest.raises(AttributeError):
        closure.workflow_state = workflow.state

    assert (
        closure.closure_id,
        closure.technician,
        closure.reason,
        closure.workflow_state,
    ) == original


def test_failed_workflow_mutation_does_not_change_workflow_identity():
    workflow, closure = build_resolved_closure()

    original = closure.workflow

    with pytest.raises(AttributeError):
        closure.workflow = TechnicianWorkflow(DiagnosticCase())

    assert closure.workflow is original
    assert closure.workflow_id == workflow.workflow_id


def test_failed_case_id_mutation_does_not_change_case_identity():
    workflow, closure = build_resolved_closure()

    original = closure.case_id

    with pytest.raises(AttributeError):
        closure.case_id = "different-case"

    assert closure.case_id == original
    assert closure.workflow.case.case_id == original


def test_failed_workflow_id_mutation_does_not_change_workflow_identity():
    workflow, closure = build_resolved_closure()

    original = closure.workflow_id

    with pytest.raises(AttributeError):
        closure.workflow_id = "different-workflow"

    assert closure.workflow_id == original
    assert closure.workflow.workflow_id == original


def test_read_only_properties_remain_stable_after_reopen():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.created_at,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.case_id,
        closure.workflow_id,
    )

    workflow.reopen()

    assert (
        closure.closure_id,
        closure.created_at,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.case_id,
        closure.workflow_id,
    ) == original


def test_read_only_properties_remain_stable_after_second_resolution():
    workflow, closure = build_resolved_closure()

    original = (
        closure.closure_id,
        closure.created_at,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.case_id,
        closure.workflow_id,
    )

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert (
        closure.closure_id,
        closure.created_at,
        closure.technician,
        closure.reason,
        closure.workflow_state,
        closure.case_id,
        closure.workflow_id,
    ) == original