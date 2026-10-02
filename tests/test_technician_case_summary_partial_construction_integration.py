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


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def add_finding(workflow):
    workflow.case.findings.append(
        Finding(
            "MEMORY_PRESSURE",
            "MEMORY",
            "HIGH",
            "High memory usage detected.",
        )
    )


def add_root_cause(workflow):
    workflow.case.root_causes.append(
        RootCauseCandidate(
            cause="Insufficient available memory",
            category="MEMORY",
            confidence=0.90,
            evidence=[],
            reason="Memory pressure is supported by diagnostic evidence.",
        )
    )


def add_recommendation(workflow):
    workflow.case.recommendations.append(
        Recommendation(
            "memory-review",
            "Review memory usage",
            "MEDIUM",
            "Review applications consuming significant memory.",
            "Reducing unnecessary memory pressure may improve responsiveness.",
        )
    )


def add_reasoning(workflow):
    recovery_history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )

    return recovery_history, reasoning_summary


def add_decision(workflow):
    decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.ACCEPT,
        "Proceed with the recommendation.",
    )

    return decision


def test_empty_case_is_valid_partial_summary():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.workflow is workflow
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.notes == []
    assert summary.reasoning_summary is None
    assert summary.decision is None


def test_finding_only_case_is_valid():
    workflow = build_workflow()
    add_finding(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert len(summary.findings) == 1
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.reasoning_summary is None
    assert summary.decision is None


def test_root_cause_only_case_is_valid():
    workflow = build_workflow()
    add_root_cause(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert len(summary.root_causes) == 1
    assert summary.recommendations == []
    assert summary.reasoning_summary is None
    assert summary.decision is None


def test_recommendation_only_case_is_valid():
    workflow = build_workflow()
    add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert len(summary.recommendations) == 1
    assert summary.reasoning_summary is None
    assert summary.decision is None


def test_notes_only_surface_is_independent():
    workflow = build_workflow()

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician opened the case.")

    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.notes == []

    assert len(notes.notes) == 1
    assert notes.workflow is workflow


def test_reasoning_can_exist_before_recovery_cycles():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    recovery_history, reasoning_summary = add_reasoning(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    assert summary.reasoning_summary is reasoning_summary
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 1

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.decision is None


def test_recovery_history_can_be_populated_after_reasoning_exists():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    recovery_history, reasoning_summary = add_reasoning(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    assert len(recovery_history.cycles) == 1

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert summary.reasoning_summary is reasoning_summary
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(recovery_history.cycles) == 2


def test_decision_can_be_added_after_initial_empty_summary():
    workflow = build_workflow()
    add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.decision is None

    decision = add_decision(workflow)
    summary._decision = decision

    assert summary.decision is decision
    assert summary.decision.workflow is workflow
    assert summary.decision.recommendation is workflow.case.recommendations[0]


def test_diagnostics_can_be_added_after_summary_creation():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_partial_surface_reads_remain_safe_during_incremental_construction():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.notes == []
    assert summary.reasoning_summary is None
    assert summary.decision is None

    add_finding(workflow)

    assert len(summary.findings) == 1
    assert summary.root_causes == []
    assert summary.recommendations == []

    add_root_cause(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert summary.recommendations == []

    add_recommendation(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_complete_surface_can_be_assembled_incrementally():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Initial observation.")

    add_finding(workflow)

    assert len(summary.findings) == 1
    assert summary.root_causes == []
    assert summary.recommendations == []

    add_root_cause(workflow)

    assert len(summary.root_causes) == 1
    assert summary.recommendations == []

    add_recommendation(workflow)

    recovery_history, reasoning_summary = add_reasoning(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    decision = add_decision(workflow)
    summary._decision = decision

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert summary.notes == []
    assert summary.reasoning_summary is reasoning_summary
    assert summary.decision is decision

    assert notes.workflow is workflow
    assert recovery_history.workflow is workflow


def test_adding_notes_does_not_complete_or_change_diagnostic_surfaces():
    workflow = build_workflow()
    add_finding(workflow)

    summary = TechnicianCaseSummary(workflow)

    findings_before = summary.findings

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician note.")

    assert summary.findings == findings_before
    assert len(summary.findings) == 1
    assert summary.root_causes == []
    assert summary.recommendations == []
    assert summary.decision is None


def test_adding_recovery_does_not_complete_or_change_diagnostics():
    workflow = build_workflow()
    add_finding(workflow)

    summary = TechnicianCaseSummary(workflow)

    findings_before = summary.findings

    recovery_history, reasoning_summary = add_reasoning(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert summary.findings == findings_before
    assert len(summary.findings) == 1
    assert summary.root_causes == []
    assert summary.recommendations == []

    assert summary.reasoning_summary is reasoning_summary
    assert len(recovery_history.cycles) == 2


def test_adding_decision_does_not_change_partial_diagnostics():
    workflow = build_workflow()
    add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    recommendations_before = summary.recommendations

    decision = add_decision(workflow)
    summary._decision = decision

    assert summary.recommendations == recommendations_before
    assert len(summary.recommendations) == 1
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.decision is decision


def test_repeated_reads_during_partial_construction_do_not_create_records():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    for _ in range(10):
        _ = summary.findings
        _ = summary.root_causes
        _ = summary.recommendations
        _ = summary.notes
        _ = summary.reasoning_summary
        _ = summary.decision

    add_finding(workflow)

    for _ in range(10):
        _ = summary.findings
        _ = summary.root_causes
        _ = summary.recommendations
        _ = summary.notes
        _ = summary.reasoning_summary
        _ = summary.decision

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 0
    assert len(workflow.case.recommendations) == 0


def test_partial_construction_preserves_workflow_identity_everywhere():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    notes = TechnicianCaseNotes(workflow)
    recovery_history, reasoning_summary = add_reasoning(workflow)

    summary.set_reasoning_summary(reasoning_summary)

    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    decision = add_decision(workflow)
    summary._decision = decision

    assert summary.workflow is workflow
    assert notes.workflow is workflow
    assert recovery_history.workflow is workflow
    assert reasoning_summary.workflow is workflow
    assert decision.workflow is workflow

    assert reasoning_summary.cycle_history is recovery_history
    assert decision.recommendation is workflow.case.recommendations[0]


def test_final_partial_to_complete_transition_has_no_cross_surface_contamination():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Initial note.")

    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    recovery_history, reasoning_summary = add_reasoning(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    decision = add_decision(workflow)
    summary._decision = decision

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert summary.notes == []
    assert summary.reasoning_summary is reasoning_summary
    assert summary.decision is decision

    assert len(notes.notes) == 1
    assert len(recovery_history.cycles) == 2

    assert summary.findings[0] is workflow.case.findings[0]
    assert summary.root_causes[0] is workflow.case.root_causes[0]
    assert summary.recommendations[0] is workflow.case.recommendations[0]

