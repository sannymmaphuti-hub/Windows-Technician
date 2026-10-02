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

    return TechnicianWorkflow(case)


def build_surface(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Initial technician observation.")

    recovery_history = TechnicianRecoveryCycleHistory(workflow)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )

    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.ACCEPT,
        "Proceed with the recommendation.",
    )

    summary._decision = decision

    return summary, notes, recovery_history, decision


def test_diagnostic_reads_are_snapshots():
    workflow = build_workflow()
    summary, _, _, _ = build_surface(workflow)

    findings_snapshot = summary.findings
    root_causes_snapshot = summary.root_causes
    recommendations_snapshot = summary.recommendations

    workflow.case.findings.append(
        Finding(
            "SECOND_FINDING",
            "TEST",
            "MEDIUM",
            "Second finding.",
        )
    )

    workflow.case.root_causes.append(
        RootCauseCandidate(
            cause="Second root cause",
            category="TEST",
            confidence=0.70,
            evidence=[],
            reason="Additional evidence.",
        )
    )

    workflow.case.recommendations.append(
        Recommendation(
            "second-recommendation",
            "Second recommendation",
            "LOW",
            "Second recommendation description.",
            "Second recommendation rationale.",
        )
    )

    assert len(findings_snapshot) == 1
    assert len(root_causes_snapshot) == 1
    assert len(recommendations_snapshot) == 1

    assert len(summary.findings) == 2
    assert len(summary.root_causes) == 2
    assert len(summary.recommendations) == 2


def test_repeated_diagnostic_reads_reflect_current_case_without_duplication():
    workflow = build_workflow()
    summary, _, _, _ = build_surface(workflow)

    assert len(summary.findings) == 1

    workflow.case.findings.append(
        Finding(
            "SECOND_FINDING",
            "TEST",
            "LOW",
            "Additional finding.",
        )
    )

    first_read = summary.findings
    second_read = summary.findings
    third_read = summary.findings

    assert len(first_read) == 2
    assert len(second_read) == 2
    assert len(third_read) == 2

    assert first_read is not second_read
    assert second_read is not third_read


def test_mutating_diagnostic_snapshot_does_not_mutate_case():
    workflow = build_workflow()
    summary, _, _, _ = build_surface(workflow)

    findings_snapshot = summary.findings
    findings_snapshot.clear()

    assert len(findings_snapshot) == 0
    assert len(workflow.case.findings) == 1
    assert len(summary.findings) == 1


def test_mutating_root_cause_snapshot_does_not_mutate_case():
    workflow = build_workflow()
    summary, _, _, _ = build_surface(workflow)

    root_causes_snapshot = summary.root_causes
    root_causes_snapshot.clear()

    assert len(root_causes_snapshot) == 0
    assert len(workflow.case.root_causes) == 1
    assert len(summary.root_causes) == 1


def test_mutating_recommendation_snapshot_does_not_mutate_case():
    workflow = build_workflow()
    summary, _, _, _ = build_surface(workflow)

    recommendations_snapshot = summary.recommendations
    recommendations_snapshot.clear()

    assert len(recommendations_snapshot) == 0
    assert len(workflow.case.recommendations) == 1
    assert len(summary.recommendations) == 1


def test_notes_remain_separate_from_summary_diagnostic_snapshots():
    workflow = build_workflow()
    summary, notes, _, _ = build_surface(workflow)

    findings_snapshot = summary.findings
    root_causes_snapshot = summary.root_causes
    recommendations_snapshot = summary.recommendations

    notes.add_note("Second technician observation.")

    assert len(notes.notes) == 2
    assert len(findings_snapshot) == 1
    assert len(root_causes_snapshot) == 1
    assert len(recommendations_snapshot) == 1


def test_recovery_history_is_shared_through_reasoning_summary():
    workflow = build_workflow()
    summary, _, recovery_history, _ = build_surface(workflow)

    assert summary.reasoning_summary.cycle_history is recovery_history

    cycles_before = list(recovery_history.cycles)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    assert summary.reasoning_summary.cycle_history is recovery_history
    assert len(cycles_before) == 2
    assert len(recovery_history.cycles) == 3


def test_recovery_history_does_not_appear_in_diagnostic_snapshots():
    workflow = build_workflow()
    summary, _, recovery_history, _ = build_surface(workflow)

    findings_before = list(summary.findings)
    root_causes_before = list(summary.root_causes)
    recommendations_before = list(summary.recommendations)

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    assert summary.findings == findings_before
    assert summary.root_causes == root_causes_before
    assert summary.recommendations == recommendations_before


def test_decision_remains_stable_when_diagnostic_content_changes():
    workflow = build_workflow()
    summary, _, _, decision = build_surface(workflow)

    workflow.case.findings.append(
        Finding(
            "SECOND_FINDING",
            "TEST",
            "MEDIUM",
            "Additional finding.",
        )
    )

    assert summary.decision is decision
    assert decision.workflow is workflow
    assert decision.recommendation is workflow.case.recommendations[0]


def test_decision_remains_separate_from_notes():
    workflow = build_workflow()
    summary, notes, _, decision = build_surface(workflow)

    notes.add_note("Additional note.")

    assert summary.decision is decision
    assert len(notes.notes) == 2


def test_replacing_decision_does_not_change_diagnostic_snapshots():
    workflow = build_workflow()
    summary, _, _, original_decision = build_surface(workflow)

    findings_before = summary.findings
    root_causes_before = summary.root_causes
    recommendations_before = summary.recommendations

    replacement_decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.DEFER,
        "Deferred for further review.",
    )

    summary._decision = replacement_decision

    assert summary.decision is replacement_decision
    assert summary.decision is not original_decision

    assert summary.findings == findings_before
    assert summary.root_causes == root_causes_before
    assert summary.recommendations == recommendations_before


def test_all_surfaces_remain_independent_after_multiple_mutations():
    workflow = build_workflow()
    summary, notes, recovery_history, original_decision = build_surface(
        workflow
    )

    findings_snapshot = summary.findings
    root_causes_snapshot = summary.root_causes
    recommendations_snapshot = summary.recommendations

    notes.add_note("Second note.")

    recovery_history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    workflow.case.findings.append(
        Finding(
            "SECOND_FINDING",
            "TEST",
            "LOW",
            "Second finding.",
        )
    )

    workflow.case.root_causes.append(
        RootCauseCandidate(
            cause="Second root cause",
            category="TEST",
            confidence=0.60,
            evidence=[],
            reason="Additional evidence.",
        )
    )

    workflow.case.recommendations.append(
        Recommendation(
            "second-recommendation",
            "Second recommendation",
            "LOW",
            "Second recommendation description.",
            "Second recommendation rationale.",
        )
    )

    replacement_decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[1],
        TechnicianDecisionType.INVESTIGATE_FURTHER,
        "Investigate the new evidence.",
    )

    summary._decision = replacement_decision

    assert len(findings_snapshot) == 1
    assert len(root_causes_snapshot) == 1
    assert len(recommendations_snapshot) == 1

    assert len(summary.findings) == 2
    assert len(summary.root_causes) == 2
    assert len(summary.recommendations) == 2

    assert len(notes.notes) == 2
    assert len(recovery_history.cycles) == 3

    assert summary.decision is replacement_decision
    assert summary.decision is not original_decision

    assert summary.reasoning_summary.cycle_history is recovery_history


def test_repeated_complete_surface_reads_do_not_create_records():
    workflow = build_workflow()
    summary, notes, recovery_history, decision = build_surface(workflow)

    for _ in range(20):
        summary.findings
        summary.root_causes
        summary.recommendations
        summary.notes
        summary.workflow_history
        summary.reasoning_summary
        summary.decision

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1
    assert len(notes.notes) == 1
    assert len(recovery_history.cycles) == 2
    assert summary.decision is decision


def test_complete_surface_snapshots_preserve_domain_separation():
    workflow = build_workflow()
    summary, notes, recovery_history, decision = build_surface(workflow)

    findings = summary.findings
    root_causes = summary.root_causes
    recommendations = summary.recommendations

    assert findings[0] is workflow.case.findings[0]
    assert root_causes[0] is workflow.case.root_causes[0]
    assert recommendations[0] is workflow.case.recommendations[0]

    assert decision.workflow is workflow
    assert recovery_history.workflow is workflow
    assert summary.reasoning_summary.workflow is workflow

    assert summary.reasoning_summary.cycle_history is recovery_history

    assert summary.notes == []
    assert len(notes.notes) == 1


def test_final_snapshot_consistency_after_long_mutation_sequence():
    workflow = build_workflow()
    summary, notes, recovery_history, decision = build_surface(workflow)

    initial_findings = summary.findings
    initial_root_causes = summary.root_causes
    initial_recommendations = summary.recommendations

    for index in range(2, 6):
        workflow.case.findings.append(
            Finding(
                f"FINDING_{index}",
                "TEST",
                "LOW",
                f"Finding {index}.",
            )
        )

        workflow.case.root_causes.append(
            RootCauseCandidate(
                cause=f"Root cause {index}",
                category="TEST",
                confidence=0.60,
                evidence=[],
                reason=f"Reason {index}.",
            )
        )

        workflow.case.recommendations.append(
            Recommendation(
                f"recommendation-{index}",
                f"Recommendation {index}",
                "LOW",
                f"Description {index}.",
                f"Rationale {index}.",
            )
        )

        notes.add_note(f"Technician note {index}.")

        recovery_history.record_cycle(
            TechnicianRecoveryCycle(
                workflow,
                cycle_number=index,
            )
        )

    assert len(initial_findings) == 1
    assert len(initial_root_causes) == 1
    assert len(initial_recommendations) == 1

    assert len(summary.findings) == 5
    assert len(summary.root_causes) == 5
    assert len(summary.recommendations) == 5

    assert len(notes.notes) == 5
    assert len(recovery_history.cycles) == 6

    assert summary.decision is decision
    assert summary.reasoning_summary.cycle_history is recovery_history