from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(
        TechnicianReasoningSummary(workflow, history)
    )
    return summary


def build_recommendation():
    from engine.recommendation import Recommendation

    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def build_decision(workflow):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Recommendation accepted.",
    )


def build_notes(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician investigated the issue.")
    return notes


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


def set_summary_state(summary, workflow):
    summary.set_decision(build_decision(workflow))
    summary.set_notes(build_notes(workflow))
    summary.set_remediation_status("COMPLETED")
    summary.set_verification_status("VERIFIED")
    summary.set_escalation_status("NOT_ESCALATED")


def summary_snapshot(summary):
    return {
        "case_id": summary.case_id,
        "workflow_id": summary.workflow_id,
        "decision_id": summary.decision.decision_id
        if summary.decision
        else None,
        "notes": [
            (note.note_id, note.text, note.workflow_state)
            for note in summary.notes
        ],
        "remediation_status": summary.remediation_status,
        "verification_status": summary.verification_status,
        "escalation_status": summary.escalation_status,
        "reasoning_summary": summary.reasoning_summary.overview,
        "closure_id": summary.closure_id,
    }


def test_summary_reasoning_summary_uses_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    assert summary.reasoning_summary.cycle_history is history


def test_summary_recovery_history_uses_same_workflow():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    assert summary.reasoning_summary.workflow is workflow
    assert history.workflow is workflow


def test_summary_starts_with_cycle_zero():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    assert summary.reasoning_summary.cycle_history.cycle_count == 1
    assert (
        summary.reasoning_summary.cycle_history.latest_cycle.cycle_number
        == 0
    )


def test_recorded_cycle_is_visible_through_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert (
        summary.reasoning_summary.cycle_history.latest_cycle
        is cycle
    )


def test_recorded_cycle_updates_summary_history_count():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert (
        summary.reasoning_summary.cycle_history.cycle_count
        == 2
    )


def test_recorded_cycle_does_not_change_summary_identity():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    summary_identity = id(summary)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert id(summary) == summary_identity


def test_recorded_cycle_does_not_change_case_identity():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    case_id_before = summary.case_id

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.case_id == case_id_before


def test_recorded_cycle_does_not_change_workflow_identity():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    workflow_id_before = summary.workflow_id

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.workflow_id == workflow_id_before
    assert summary.workflow is workflow


def test_recorded_cycle_does_not_change_decision():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)
    summary.set_decision(build_decision(workflow))

    decision_before = summary.decision

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.decision is decision_before


def test_recorded_cycle_does_not_change_notes():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)
    summary.set_notes(build_notes(workflow))

    notes_before = [
        (note.note_id, note.text, note.workflow_state)
        for note in summary.notes
    ]

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert [
        (note.note_id, note.text, note.workflow_state)
        for note in summary.notes
    ] == notes_before


def test_recorded_cycle_does_not_change_operational_statuses():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)
    set_summary_state(summary, workflow)

    statuses_before = (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    )

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    ) == statuses_before


def test_recorded_cycle_does_not_change_reasoning_overview():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    overview_before = summary.reasoning_summary.overview

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.reasoning_summary.overview == overview_before


def test_recorded_cycle_does_not_create_closure():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.closure is None


def test_closure_and_recovery_history_can_coexist():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert summary.closure is closure
    assert summary.reasoning_summary.cycle_history.latest_cycle is cycle


def test_reopening_preserves_recovery_history_in_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    resolve_workflow(workflow)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    workflow.reopen()

    assert summary.reasoning_summary.cycle_history.cycle_count == 2
    assert summary.reasoning_summary.cycle_history.latest_cycle is cycle
    assert summary.workflow_state.value == "INVESTIGATING"


def test_multiple_recovery_cycles_remain_visible_in_summary():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycles = [
        TechnicianRecoveryCycle(workflow, cycle_number=1),
        TechnicianRecoveryCycle(workflow, cycle_number=2),
        TechnicianRecoveryCycle(workflow, cycle_number=3),
    ]

    for cycle in cycles:
        history.record_cycle(cycle)

    assert [
        cycle.cycle_number
        for cycle in summary.reasoning_summary.cycle_history.cycles
    ] == [0, 1, 2, 3]


def test_recovery_history_does_not_become_summary_diagnostic_reasoning():
    workflow = build_workflow()
    history = build_history(workflow)
    summary = build_summary(workflow, history)

    cycle = TechnicianRecoveryCycle(workflow, cycle_number=1)
    history.record_cycle(cycle)

    assert cycle not in summary.findings
    assert cycle not in summary.root_causes
    assert cycle not in summary.recommendations
    assert cycle not in summary.reasoning_summary.correlations