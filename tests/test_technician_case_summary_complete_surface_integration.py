from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.root_cause import RootCauseCandidate
from engine.recommendation import Recommendation
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow


def build_case():
    case = DiagnosticCase()

    case.findings.append(
        Finding(
            "MEMORY_PRESSURE",
            "MEMORY",
            "HIGH",
            "High memory usage detected.",
        )
    )

    case.root_causes.append(
        RootCauseCandidate(
            cause="Insufficient available memory",
            category="MEMORY",
            confidence=0.90,
            evidence=[],
            reason="Memory pressure is supported by the diagnostic evidence.",
        )
    )

    case.recommendations.append(
        Recommendation(
            "memory-review",
            "Review memory usage",
            "MEDIUM",
            "Review applications consuming significant memory.",
            "Reducing unnecessary memory pressure may improve system responsiveness.",
        )
    )

    return case


def build_workflow():
    return TechnicianWorkflow(build_case())


def build_reasoning_summary(workflow, recovery_history):
    return TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )


def build_complete_surface(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician observed elevated memory usage.")

    recovery_history = TechnicianRecoveryCycleHistory(workflow)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )
    recovery_history.record_cycle(cycle)

    reasoning_summary = build_reasoning_summary(
        workflow,
        recovery_history,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    recommendation = workflow.case.recommendations[0]

    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        "Proceed with the recommended review.",
    )

    summary._decision = decision

    return (
        summary,
        notes,
        recovery_history,
        decision,
    )


def continue_investigation(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

def test_complete_summary_exposes_all_major_surfaces():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    # TechnicianCaseSummary does not automatically discover
    # a separate TechnicianCaseNotes instance.
    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision

    assert summary.reasoning_summary is not None
    assert summary.reasoning_summary.cycle_history is recovery_history


def test_notes_do_not_change_diagnostic_content():
    workflow = build_workflow()

    summary, notes, _, _ = build_complete_surface(workflow)

    findings_before = summary.findings
    root_causes_before = summary.root_causes
    recommendations_before = summary.recommendations

    notes.add_note("Additional technician observation.")

    assert summary.findings == findings_before
    assert summary.root_causes == root_causes_before
    assert summary.recommendations == recommendations_before


def test_diagnostic_content_does_not_change_notes():
    workflow = build_workflow()

    summary, notes, _, _ = build_complete_surface(workflow)

    notes_before = notes.notes

    workflow.case.findings.append(
        Finding(
            "SECOND_FINDING",
            "TEST",
            "MEDIUM",
            "Second diagnostic finding.",
        )
    )

    assert notes.notes == notes_before
    assert len(summary.findings) == 2


def test_recovery_history_does_not_change_decision():
    workflow = build_workflow()

    summary, _, recovery_history, decision = build_complete_surface(workflow)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )
    recovery_history.record_cycle(cycle)

    assert summary.decision is decision
    assert decision.workflow is workflow
    assert decision.recommendation is workflow.case.recommendations[0]
    assert len(recovery_history.cycles) == 3


def test_decision_does_not_change_recovery_history():
    workflow = build_workflow()

    summary, _, recovery_history, decision = build_complete_surface(workflow)

    cycles_before = list(recovery_history.cycles)

    replacement_decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.DEFER,
        "Deferred for additional evidence.",
    )

    summary._decision = replacement_decision

    assert summary.decision is replacement_decision
    assert recovery_history.cycles == cycles_before
    assert decision.workflow is workflow


def test_complete_surface_survives_full_lifecycle():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    continue_investigation(workflow)
    workflow.resolve()

    assert workflow.is_terminal is True
    assert summary.workflow_state == workflow.state

    assert summary.findings
    assert summary.root_causes
    assert summary.recommendations

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2


def test_complete_surface_survives_reopen():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    continue_investigation(workflow)
    workflow.resolve()
    workflow.reopen()

    assert workflow.state.name == "INVESTIGATING"

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2

    assert summary.findings
    assert summary.root_causes
    assert summary.recommendations


def test_complete_surface_survives_reinvestigation():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    continue_investigation(workflow)
    workflow.resolve()
    workflow.reopen()

    continue_investigation(workflow)
    workflow.resolve()

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2


def test_complete_surface_survives_escalation():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    workflow.escalate()

    assert workflow.is_terminal is True
    assert summary.workflow_state == workflow.state

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2

    assert summary.findings
    assert summary.root_causes
    assert summary.recommendations


def test_failed_workflow_operation_preserves_complete_surface():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    try:
        workflow.start_remediation()
    except ValueError:
        pass

    assert summary.workflow_state == workflow.state

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2

    assert summary.findings
    assert summary.root_causes
    assert summary.recommendations


def test_repeated_summary_reads_do_not_duplicate_any_surface():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    for _ in range(10):
        assert summary.findings
        assert summary.root_causes
        assert summary.recommendations

        assert summary.notes == []
        assert len(notes.notes) == 1

        assert summary.decision is decision
        assert summary.reasoning_summary.cycle_history is recovery_history

    assert len(recovery_history.cycles) == 2
    assert len(notes.notes) == 1
    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1


def test_multiple_recovery_cycles_remain_separate_from_complete_surface():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    for cycle_number in range(2, 11):
        recovery_history.record_cycle(
            TechnicianRecoveryCycle(
                workflow,
                cycle_number=cycle_number,
            )
        )

    assert len(recovery_history.cycles) == 11

    assert [cycle.cycle_number for cycle in recovery_history.cycles] == list(
        range(11)
    )

    assert summary.reasoning_summary.cycle_history is recovery_history

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_recovery_cycles_do_not_become_diagnostic_content():
    workflow = build_workflow()

    summary, _, recovery_history, _ = build_complete_surface(workflow)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    assert len(recovery_history.cycles) == 3
    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_notes_do_not_become_diagnostic_content():
    workflow = build_workflow()

    summary, notes, _, _ = build_complete_surface(workflow)

    notes.add_note("This is an operational technician note.")

    assert len(notes.notes) == 2
    assert summary.notes == []

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_diagnostic_content_does_not_become_recovery_history():
    workflow = build_workflow()

    summary, _, recovery_history, _ = build_complete_surface(workflow)

    workflow.case.findings.append(
        Finding(
            "THIRD_FINDING",
            "TEST",
            "LOW",
            "Additional finding.",
        )
    )

    assert len(summary.findings) == 2
    assert len(recovery_history.cycles) == 2


def test_complete_surface_preserves_identity_relationships():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    assert summary.workflow is workflow
    assert decision.workflow is workflow
    assert recovery_history.workflow is workflow
    assert summary.reasoning_summary.workflow is workflow

    assert summary.reasoning_summary.cycle_history is recovery_history

    assert summary.recommendations[0] is workflow.case.recommendations[0]
    assert decision.recommendation is workflow.case.recommendations[0]

    assert len(notes.notes) == 1


def test_complete_surface_final_consistency_after_long_sequence():
    workflow = build_workflow()

    summary, notes, recovery_history, decision = build_complete_surface(
        workflow
    )

    continue_investigation(workflow)
    workflow.resolve()

    for cycle_number in range(2, 6):
        recovery_history.record_cycle(
            TechnicianRecoveryCycle(
                workflow,
                cycle_number=cycle_number,
            )
        )

    workflow.reopen()

    continue_investigation(workflow)
    workflow.resolve()

    assert workflow.is_terminal is True

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id
    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert summary.notes == []
    assert len(notes.notes) == 1

    assert summary.decision is decision

    assert summary.reasoning_summary is not None
    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.cycle_history is recovery_history

    assert len(recovery_history.cycles) == 6

    assert [cycle.cycle_number for cycle in recovery_history.cycles] == list(
        range(6)
    )

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1