from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
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


def build_summary(workflow):
    return TechnicianCaseSummary(workflow)


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


def test_attaching_same_closure_twice_is_idempotent():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)
    summary.set_closure(closure)

    assert summary.closure is closure


def test_attaching_same_closure_does_not_change_closure_id():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)
    closure_id_before = summary.closure_id

    summary.set_closure(closure)

    assert summary.closure_id == closure_id_before


def test_attaching_same_closure_does_not_change_created_at():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary.set_closure(closure)
    created_at_before = summary.closure.created_at

    summary.set_closure(closure)

    assert summary.closure.created_at == created_at_before


def test_attaching_same_closure_does_not_change_technician():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        technician="Primary Technician",
    )

    summary.set_closure(closure)
    technician_before = summary.closure_technician

    summary.set_closure(closure)

    assert summary.closure_technician == technician_before


def test_attaching_same_closure_does_not_change_reason():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(
        workflow,
        reason="Verified resolution after remediation.",
    )

    summary.set_closure(closure)
    reason_before = summary.closure_reason

    summary.set_closure(closure)

    assert summary.closure_reason == reason_before


def test_attaching_same_closure_does_not_change_summary_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    summary_identity = id(summary)

    summary.set_closure(closure)
    summary.set_closure(closure)

    assert id(summary) == summary_identity


def test_first_closure_is_current_closure_after_first_attachment():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First closure.",
    )

    summary.set_closure(first)

    assert summary.closure is first


def test_second_closure_replaces_first_closure():
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


def test_replacement_updates_closure_id_only_to_new_record():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure.",
    )

    summary.set_closure(first)
    first_id = summary.closure_id

    summary.set_closure(second)

    assert summary.closure_id == second.closure_id
    assert summary.closure_id != first_id


def test_replacement_updates_technician_to_new_record():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
    )
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.closure_technician == "Second Technician"


def test_replacement_updates_reason_to_new_record():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        reason="First closure reason.",
    )
    second = build_closure(
        workflow,
        reason="Second closure reason.",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.closure_reason == "Second closure reason."


def test_replacement_does_not_mutate_first_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(
        workflow,
        technician="First Technician",
        reason="First closure.",
    )
    first_id = first.closure_id
    first_created_at = first.created_at
    first_technician = first.technician
    first_reason = first.reason
    first_state = first.workflow_state

    second = build_closure(
        workflow,
        technician="Second Technician",
        reason="Second closure.",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert first.closure_id == first_id
    assert first.created_at == first_created_at
    assert first.technician == first_technician
    assert first.reason == first_reason
    assert first.workflow_state is first_state


def test_replacement_does_not_duplicate_closure_reference():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.closure is second
    assert summary.closure is not first


def test_replacing_closure_does_not_change_workflow_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    summary.set_closure(first)
    state_before = workflow.state

    summary.set_closure(second)

    assert workflow.state is state_before


def test_replacing_closure_does_not_change_workflow_history():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    summary.set_closure(first)
    history_before = list(workflow.history)

    summary.set_closure(second)

    assert workflow.history == history_before


def test_replacing_closure_does_not_change_case_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    case_id_before = summary.case_id

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.case_id == case_id_before
    assert second.case_id == case_id_before


def test_replacing_closure_keeps_current_closure_workflow_reference():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    second = build_closure(
        workflow,
        technician="Second Technician",
    )

    summary.set_closure(first)
    summary.set_closure(second)

    assert summary.closure.workflow is workflow
    assert summary.closure.workflow_id == workflow.workflow_id


def test_reopening_after_replacement_keeps_current_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first = build_closure(workflow)
    summary.set_closure(first)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second = build_closure(
        workflow,
        technician="Second Technician",
    )
    summary.set_closure(second)

    workflow.reopen()

    assert summary.closure is second
    assert summary.closure_technician == "Second Technician"
    assert summary.closure_reason == "Issue resolved and verified."
    assert summary.workflow_state.value == "INVESTIGATING"


def test_multiple_replacements_leave_exactly_one_current_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    closures = [
        build_closure(
            workflow,
            technician=f"Technician {index}",
            reason=f"Closure {index}.",
        )
        for index in range(1, 5)
    ]

    for closure in closures:
        summary.set_closure(closure)

    assert summary.closure is closures[-1]
    assert summary.closure_id == closures[-1].closure_id
    assert summary.closure_technician == closures[-1].technician
    assert summary.closure_reason == closures[-1].reason