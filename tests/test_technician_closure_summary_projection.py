from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_summary(workflow):
    return TechnicianCaseSummary(workflow)


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


def test_summary_has_no_closure_initially():
    workflow = build_workflow()
    summary = build_summary(workflow)

    assert summary.closure is None
    assert summary.closure_id is None
    assert summary.closure_technician is None
    assert summary.closure_reason is None
    assert summary.closure_state is None


def test_summary_projects_exact_closure_object():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure is closure


def test_summary_projects_closure_id_exactly():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure_id == closure.closure_id


def test_summary_projects_closure_technician_exactly():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        technician="Primary Technician",
    )

    summary.set_closure(closure)

    assert summary.closure_technician == closure.technician
    assert summary.closure_technician == "Primary Technician"


def test_summary_projects_closure_reason_exactly():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        reason="Resolution verified after remediation.",
    )

    summary.set_closure(closure)

    assert summary.closure_reason == closure.reason
    assert summary.closure_reason == (
        "Resolution verified after remediation."
    )


def test_summary_projects_closure_workflow_state_exactly():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure_state is closure.workflow_state
    assert summary.closure_state is workflow.state


def test_summary_projection_does_not_create_new_closure_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure_id == closure.closure_id
    assert summary.closure is closure


def test_summary_projection_does_not_change_closure_id():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    closure_id_before = closure.closure_id
    projected_id_before = summary.closure_id

    assert projected_id_before == closure_id_before
    assert summary.closure_id == projected_id_before


def test_summary_projection_does_not_change_closure_technician():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        technician="Primary Technician",
    )

    summary.set_closure(closure)

    technician_before = closure.technician

    assert summary.closure_technician == technician_before
    assert closure.technician == technician_before


def test_summary_projection_does_not_change_closure_reason():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        reason="Resolution verified successfully.",
    )

    summary.set_closure(closure)

    reason_before = closure.reason

    assert summary.closure_reason == reason_before
    assert closure.reason == reason_before


def test_summary_projection_does_not_change_closure_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    state_before = closure.workflow_state

    assert summary.closure_state is state_before
    assert closure.workflow_state is state_before


def test_summary_projection_survives_workflow_reopen():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        technician="Primary Technician",
        reason="Issue resolved and verified.",
    )

    summary.set_closure(closure)

    closure_id = closure.closure_id
    technician = closure.technician
    reason = closure.reason
    closure_state = closure.workflow_state

    workflow.reopen()

    assert summary.closure is closure
    assert summary.closure_id == closure_id
    assert summary.closure_technician == technician
    assert summary.closure_reason == reason
    assert summary.closure_state is closure_state


def test_summary_projection_reflects_current_attached_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First closure.",
    )
    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure.",
    )

    summary.set_closure(first)

    assert summary.closure is first
    assert summary.closure_id == first.closure_id

    summary.set_closure(second)

    assert summary.closure is second
    assert summary.closure_id == second.closure_id
    assert summary.closure_technician == second.technician
    assert summary.closure_reason == second.reason


def test_summary_projection_does_not_retain_replaced_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First closure.",
    )
    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure.",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.closure is second
    assert summary.closure is not first
    assert summary.closure_id != first.closure_id


def test_summary_projection_preserves_closure_workflow_reference():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    assert summary.closure.workflow is workflow
    assert summary.closure.workflow_id == workflow.workflow_id
    assert summary.workflow is workflow


def test_summary_projection_remains_consistent_after_re_resolution():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        technician="Original Technician",
        reason="Original verified closure.",
    )

    summary.set_closure(closure)

    original_id = summary.closure_id
    original_technician = summary.closure_technician
    original_reason = summary.closure_reason
    original_state = summary.closure_state

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.closure_id == original_id
    assert summary.closure_technician == original_technician
    assert summary.closure_reason == original_reason
    assert summary.closure_state is original_state


def test_summary_projection_is_not_derived_from_workflow_current_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)

    workflow.reopen()

    assert summary.workflow_state.value == "INVESTIGATING"
    assert summary.closure_state.value == "RESOLVED"
    assert summary.closure.workflow_state.value == "RESOLVED"