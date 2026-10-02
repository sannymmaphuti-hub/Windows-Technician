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


def build_closure(workflow, technician="Test Technician"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason="Issue resolved and verified.",
    )


def set_statuses(summary):
    summary.set_remediation_status("COMPLETED")
    summary.set_verification_status("VERIFIED")
    summary.set_escalation_status("NOT_ESCALATED")


def status_snapshot(summary):
    return {
        "remediation": summary.remediation_status,
        "verification": summary.verification_status,
        "escalation": summary.escalation_status,
    }


def test_closure_does_not_create_operational_status():
    workflow = build_workflow()
    summary = build_summary(workflow)

    assert summary.remediation_status is None
    assert summary.verification_status is None
    assert summary.escalation_status is None

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.remediation_status is None
    assert summary.verification_status is None
    assert summary.escalation_status is None


def test_closure_does_not_change_existing_operational_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    statuses_before = status_snapshot(summary)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert status_snapshot(summary) == statuses_before


def test_closure_does_not_change_remediation_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_remediation_status("COMPLETED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.remediation_status == "COMPLETED"


def test_closure_does_not_change_verification_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_verification_status("VERIFIED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.verification_status == "VERIFIED"


def test_closure_does_not_change_escalation_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_escalation_status("NOT_ESCALATED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.escalation_status == "NOT_ESCALATED"


def test_closure_does_not_replace_remediation_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_remediation_status("COMPLETED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.remediation_status == "COMPLETED"


def test_closure_does_not_replace_verification_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_verification_status("VERIFIED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.verification_status == "VERIFIED"


def test_closure_does_not_replace_escalation_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    summary.set_escalation_status("NOT_ESCALATED")

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.escalation_status == "NOT_ESCALATED"


def test_closure_does_not_change_status_snapshot_after_reopen():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    statuses_before = status_snapshot(summary)

    workflow.reopen()

    assert status_snapshot(summary) == statuses_before


def test_multiple_closures_do_not_change_operational_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    statuses_before = status_snapshot(summary)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = build_closure(
        workflow,
        technician="Second Technician",
    )
    summary.set_closure(second_closure)

    assert first_closure is not second_closure
    assert status_snapshot(summary) == statuses_before


def test_closure_does_not_change_summary_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    summary_identity = id(summary)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert id(summary) == summary_identity


def test_closure_does_not_change_workflow_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    workflow_id_before = workflow.workflow_id

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.workflow_id == workflow_id_before
    assert closure.workflow is workflow
    assert summary.workflow is workflow


def test_closure_does_not_change_workflow_history():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    resolve_workflow(workflow)
    history_before = list(workflow.history)

    summary.set_closure(build_closure(workflow))

    assert workflow.history == history_before


def test_closure_does_not_change_case_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    resolve_workflow(workflow)
    case_status_before = workflow.case.status

    summary.set_closure(build_closure(workflow))

    assert workflow.case.status == case_status_before


def test_operational_status_does_not_create_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    set_statuses(summary)

    assert summary.closure is None
    assert workflow.state.value == "OPEN"


def test_replacing_closure_preserves_operational_status():
    workflow = build_workflow()
    summary = build_summary(workflow)
    set_statuses(summary)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    statuses_before = status_snapshot(summary)

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Verified again after follow-up.",
    )
    summary.set_closure(second_closure)

    assert summary.closure is second_closure
    assert summary.closure is not first_closure
    assert status_snapshot(summary) == statuses_before