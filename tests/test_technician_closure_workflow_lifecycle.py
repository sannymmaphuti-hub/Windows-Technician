from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


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


def test_closure_can_exist_after_workflow_resolves():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert closure.workflow is workflow
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_closure_does_not_change_resolved_workflow_state():
    workflow = build_workflow()

    resolve_workflow(workflow)
    state_before = workflow.state

    build_closure(workflow)

    assert workflow.state is state_before
    assert workflow.state is WorkflowState.RESOLVED


def test_closure_does_not_change_workflow_history():
    workflow = build_workflow()

    resolve_workflow(workflow)
    history_before = workflow.history

    build_closure(workflow)

    assert workflow.history == history_before


def test_reopening_workflow_does_not_change_closure_record():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    closure_id_before = closure.closure_id
    technician_before = closure.technician
    reason_before = closure.reason
    closure_state_before = closure.workflow_state

    workflow.reopen()

    assert closure.closure_id == closure_id_before
    assert closure.technician == technician_before
    assert closure.reason == reason_before
    assert closure.workflow_state is closure_state_before


def test_reopening_workflow_does_not_replace_closure():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    workflow.reopen()

    assert closure.workflow is workflow
    assert closure is not None


def test_reopened_workflow_is_investigating_while_closure_remains_resolved_record():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_closure_does_not_prevent_workflow_reopen():
    workflow = build_workflow()

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_closure_does_not_create_new_workflow_history_entry():
    workflow = build_workflow()

    resolve_workflow(workflow)
    history_before_closure = workflow.history

    build_closure(workflow)

    assert workflow.history == history_before_closure

    workflow.reopen()

    assert len(workflow.history) == len(history_before_closure) + 1


def test_closure_can_remain_attached_across_reopen():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    workflow.reopen()

    assert closure.workflow is workflow
    assert closure.closure_id
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_closure_does_not_follow_workflow_state_after_reopen():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_workflow_can_be_resolved_again_after_reopen_without_mutating_original_closure():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    original_closure_id = closure.closure_id
    original_reason = closure.reason
    original_technician = closure.technician

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert closure.closure_id == original_closure_id
    assert closure.reason == original_reason
    assert closure.technician == original_technician
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_second_closure_has_independent_identity():
    workflow = build_workflow()

    resolve_workflow(workflow)
    first_closure = build_closure(workflow)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Issue resolved after recovery cycle.",
    )

    assert first_closure.closure_id != second_closure.closure_id
    assert first_closure.workflow is workflow
    assert second_closure.workflow is workflow


def test_first_closure_remains_unchanged_when_second_closure_is_created():
    workflow = build_workflow()

    resolve_workflow(workflow)
    first_closure = build_closure(workflow)

    first_id = first_closure.closure_id
    first_technician = first_closure.technician
    first_reason = first_closure.reason

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Issue resolved after recovery cycle.",
    )

    assert first_closure.closure_id == first_id
    assert first_closure.technician == first_technician
    assert first_closure.reason == first_reason
    assert second_closure.closure_id != first_closure.closure_id


def test_closure_cannot_be_created_while_workflow_is_investigating():
    workflow = build_workflow()
    workflow.start_investigation()

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed while the workflow is INVESTIGATING."
        )


def test_closure_cannot_be_created_while_workflow_is_diagnosed():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed while the workflow is DIAGNOSED."
        )


def test_closure_cannot_be_created_while_workflow_requires_action():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed while the workflow requires action."
        )


def test_closure_cannot_be_created_while_workflow_is_remediating():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed while the workflow is REMEDIATING."
        )


def test_closure_cannot_be_created_while_workflow_is_verifying():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed while the workflow is VERIFYING."
        )