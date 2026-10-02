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


def build_valid_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )


def test_valid_closure_is_accepted():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_valid_closure(workflow)

    assert closure.workflow is workflow


def test_none_workflow_is_rejected():
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=None,
            technician="Test Technician",
            reason="Issue resolved.",
        )


def test_wrong_workflow_type_is_rejected():
    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=object(),
            technician="Test Technician",
            reason="Issue resolved.",
        )


def test_non_string_technician_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician=123,
            reason="Issue resolved.",
        )


def test_empty_technician_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="",
            reason="Issue resolved.",
        )


def test_whitespace_technician_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="   ",
            reason="Issue resolved.",
        )


def test_non_string_reason_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="Test Technician",
            reason=123,
        )


def test_empty_reason_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="Test Technician",
            reason="",
        )


def test_whitespace_reason_is_rejected():
    workflow = build_workflow()
    resolve_workflow(workflow)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="Test Technician",
            reason="   ",
        )


def test_open_workflow_cannot_be_closed():
    workflow = build_workflow()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_investigating_workflow_cannot_be_closed():
    workflow = build_workflow()
    workflow.start_investigation()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_diagnosed_workflow_cannot_be_closed():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_action_required_workflow_cannot_be_closed():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_remediating_workflow_cannot_be_closed():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_verifying_workflow_cannot_be_closed():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    with pytest.raises(ValueError):
        build_valid_closure(workflow)


def test_resolved_workflow_can_be_closed():
    workflow = build_workflow()
    resolve_workflow(workflow)

    closure = build_valid_closure(workflow)

    assert closure.workflow_state.value == "RESOLVED"


def test_failed_validation_does_not_change_workflow_state():
    workflow = build_workflow()
    resolve_workflow(workflow)

    state_before = workflow.state
    history_before = list(workflow.history)

    with pytest.raises(ValueError):
        TechnicianCaseClosure(
            workflow=workflow,
            technician="",
            reason="Issue resolved.",
        )

    assert workflow.state is state_before
    assert workflow.history == history_before