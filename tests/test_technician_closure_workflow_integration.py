import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    case = DiagnosticCase()
    return TechnicianWorkflow(case)


def progress_to_resolved(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(workflow, technician="Sanny", reason="Issue resolved"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason=reason,
    )


def test_closure_rejects_open_workflow():
    workflow = build_workflow()
    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "OPEN"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_investigating_workflow():
    workflow = build_workflow()
    workflow.start_investigation()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "INVESTIGATING"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_diagnosed_workflow():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "DIAGNOSED"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_action_required_workflow():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "ACTION_REQUIRED"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_remediating_workflow():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "REMEDIATING"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_verifying_workflow():
    workflow = build_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(workflow)

    assert workflow.state.value == "VERIFYING"
    assert not workflow.is_terminal
    assert workflow.history == history_before


def test_closure_rejects_escalated_workflow():
    workflow = build_workflow()
    workflow.escalate()

    history_before = list(workflow.history)

    with pytest.raises(
        ValueError,
        match="A case can only be closed after it is RESOLVED.",
    ):
        build_closure(
            workflow,
            reason="Case escalated.",
        )

    assert workflow.state.value == "ESCALATED"
    assert workflow.is_terminal
    assert workflow.history == history_before


def test_closure_does_not_create_workflow_history():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    history_before = list(workflow.history)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.history == history_before


def test_closure_does_not_create_workflow_transition():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    state_before = workflow.state

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state is state_before
    assert workflow.state.value == "RESOLVED"


def test_resolved_workflow_remains_resolved_after_closure():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal
    assert summary.closure_state is workflow.state


def test_closure_does_not_escalate_resolved_workflow():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal


def test_closure_does_not_create_escalation_history():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    history_before = list(workflow.history)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.history == history_before
    assert workflow.state.value == "RESOLVED"


def test_resolved_closure_preserves_workflow_identity():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert closure.workflow is workflow
    assert summary.workflow is workflow
    assert summary.closure.workflow is workflow


def test_closure_reflects_resolved_workflow_state():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.closure_state is workflow.state
    assert summary.closure_state.value == "RESOLVED"


def test_closure_cannot_bind_to_different_workflow():
    workflow = build_workflow()
    other_workflow = build_workflow()

    progress_to_resolved(workflow)
    progress_to_resolved(other_workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(other_workflow)

    with pytest.raises(
        ValueError,
        match="Closure belongs to a different workflow.",
    ):
        summary.set_closure(closure)

    assert summary.closure is None


def test_closure_does_not_change_terminal_state():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.is_terminal
    assert workflow.state.value == "RESOLVED"


def test_reopening_workflow_is_explicit_after_closure():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    workflow.reopen()

    assert workflow.state.value == "INVESTIGATING"
    assert not workflow.is_terminal


def test_reopening_workflow_does_not_mutate_closure_identity():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    closure_id = closure.closure_id

    workflow.reopen()

    assert summary.closure is closure
    assert summary.closure_id == closure_id


def test_reopening_workflow_does_not_create_new_closure():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    workflow.reopen()

    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id


def test_closure_does_not_reopen_workflow():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state.value == "RESOLVED"

    summary.set_closure(closure)

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal


def test_replacing_closure_does_not_change_workflow_state():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)

    first_closure = build_closure(
        workflow,
        technician="Sanny",
        reason="First closure.",
    )
    summary.set_closure(first_closure)

    second_closure = build_closure(
        workflow,
        technician="Technician 2",
        reason="Updated closure.",
    )
    summary.set_closure(second_closure)

    assert workflow.state.value == "RESOLVED"
    assert workflow.is_terminal
    assert summary.closure is second_closure


def test_closure_is_record_not_workflow_controller():
    workflow = build_workflow()
    progress_to_resolved(workflow)

    summary = TechnicianCaseSummary(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.workflow is workflow
    assert summary.closure is closure
    assert summary.workflow_state.value == "RESOLVED"
    assert summary.closure_state.value == "RESOLVED"