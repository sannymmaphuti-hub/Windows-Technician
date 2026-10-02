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
            reason="Memory pressure is supported by diagnostic evidence.",
        )
    )

    case.recommendations.append(
        Recommendation(
            "memory-review",
            "Review memory usage",
            "MEDIUM",
            "Review applications consuming significant memory.",
            "Reducing unnecessary memory pressure may improve responsiveness.",
        )
    )

    return TechnicianWorkflow(case)


def build_complete_summary(workflow):
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

    return summary, notes, recovery_history, reasoning_summary, decision


def test_summary_exposes_workflow():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.workflow is workflow


def test_summary_exposes_current_diagnostic_findings():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == workflow.case.findings
    assert summary.findings[0] is workflow.case.findings[0]


def test_summary_exposes_current_root_causes():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.root_causes == workflow.case.root_causes
    assert summary.root_causes[0] is workflow.case.root_causes[0]


def test_summary_exposes_current_recommendations():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.recommendations == workflow.case.recommendations
    assert summary.recommendations[0] is workflow.case.recommendations[0]


def test_empty_summary_has_safe_diagnostic_collections():
    workflow = TechnicianWorkflow(DiagnosticCase())
    summary = TechnicianCaseSummary(workflow)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_empty_summary_has_safe_optional_surfaces():
    workflow = TechnicianWorkflow(DiagnosticCase())
    summary = TechnicianCaseSummary(workflow)

    assert summary.notes == []
    assert summary.reasoning_summary is None
    assert summary.decision is None


def test_summary_notes_remain_separate_from_case_diagnostics():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.notes == []

    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Technician observation.")

    assert len(notes.notes) == 1
    assert summary.findings == workflow.case.findings
    assert summary.root_causes == workflow.case.root_causes
    assert summary.recommendations == workflow.case.recommendations


def test_summary_reasoning_surface_is_explicitly_configurable():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.reasoning_summary is None

    recovery_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )

    summary.set_reasoning_summary(reasoning_summary)

    assert summary.reasoning_summary is reasoning_summary


def test_summary_decision_is_optional_until_set():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.decision is None

    decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.ACCEPT,
        "Proceed.",
    )

    summary._decision = decision

    assert summary.decision is decision


def test_complete_summary_exposes_all_major_surfaces():
    workflow = build_workflow()

    (
        summary,
        notes,
        recovery_history,
        reasoning_summary,
        decision,
    ) = build_complete_summary(workflow)

    assert summary.workflow is workflow

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert summary.notes == []
    assert summary.reasoning_summary is reasoning_summary
    assert summary.decision is decision

    assert notes.workflow is workflow
    assert recovery_history.workflow is workflow
    assert reasoning_summary.workflow is workflow
    assert decision.workflow is workflow


def test_summary_reads_do_not_create_domain_records():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    for _ in range(25):
        _ = summary.workflow
        _ = summary.findings
        _ = summary.root_causes
        _ = summary.recommendations
        _ = summary.notes
        _ = summary.reasoning_summary
        _ = summary.decision

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1


def test_summary_diagnostic_surfaces_follow_case_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    workflow.case.findings.append(
        Finding(
            "CPU_PRESSURE",
            "CPU",
            "MEDIUM",
            "CPU pressure detected.",
        )
    )

    workflow.case.root_causes.append(
        RootCauseCandidate(
            cause="CPU contention",
            category="CPU",
            confidence=0.75,
            evidence=[],
            reason="CPU evidence supports contention.",
        )
    )

    workflow.case.recommendations.append(
        Recommendation(
            "cpu-review",
            "Review CPU usage",
            "LOW",
            "Review processes consuming CPU.",
            "Reducing CPU contention may improve responsiveness.",
        )
    )

    assert len(summary.findings) == 2
    assert len(summary.root_causes) == 2
    assert len(summary.recommendations) == 2


def test_summary_does_not_duplicate_case_objects():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    first_findings = summary.findings
    second_findings = summary.findings

    first_root_causes = summary.root_causes
    second_root_causes = summary.root_causes

    first_recommendations = summary.recommendations
    second_recommendations = summary.recommendations

    assert first_findings[0] is second_findings[0]
    assert first_root_causes[0] is second_root_causes[0]
    assert first_recommendations[0] is second_recommendations[0]

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1


def test_complete_summary_preserves_domain_identity_relationships():
    workflow = build_workflow()

    (
        summary,
        notes,
        recovery_history,
        reasoning_summary,
        decision,
    ) = build_complete_summary(workflow)

    assert summary.workflow is workflow

    assert summary.findings[0] is workflow.case.findings[0]
    assert summary.root_causes[0] is workflow.case.root_causes[0]
    assert summary.recommendations[0] is workflow.case.recommendations[0]

    assert notes.workflow is workflow
    assert recovery_history.workflow is workflow
    assert reasoning_summary.workflow is workflow
    assert reasoning_summary.cycle_history is recovery_history
    assert decision.workflow is workflow
    assert decision.recommendation is workflow.case.recommendations[0]


def test_summary_remains_readable_when_optional_surfaces_are_added_later():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    assert summary.reasoning_summary is None
    assert summary.decision is None

    recovery_history = TechnicianRecoveryCycleHistory(workflow)
    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )

    summary.set_reasoning_summary(reasoning_summary)

    decision = TechnicianDecision(
        workflow,
        workflow.case.recommendations[0],
        TechnicianDecisionType.ACCEPT,
        "Proceed.",
    )

    summary._decision = decision

    assert summary.reasoning_summary is reasoning_summary
    assert summary.decision is decision

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1