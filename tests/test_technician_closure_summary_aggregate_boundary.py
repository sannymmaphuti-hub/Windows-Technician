from engine.correlation import Correlation
from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.root_cause import RootCauseCandidate
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_recommendation():
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
        notes="Recommendation accepted for remediation.",
    )


def build_notes(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note(
        "Investigated sustained memory pressure.",
    )
    return notes


def build_reasoning_data(workflow):
    workflow.case.set_findings(
        [
            Finding(
                finding_type="MEMORY_PRESSURE",
                category="MEMORY",
                severity="HIGH",
                description="Memory usage is consistently high.",
            )
        ]
    )

    workflow.case.set_correlations(
        [
            Correlation(
                correlation_type="MEMORY_PROCESS",
                findings=[
                    "MEMORY_PRESSURE",
                    "HIGH_PROCESS_MEMORY",
                ],
                strength="HIGH",
                explanation=(
                    "Memory pressure correlates with elevated "
                    "process memory usage."
                ),
            )
        ]
    )

    workflow.case.set_root_causes(
        [
            RootCauseCandidate(
                cause="Sustained memory pressure caused system instability.",
                category="MEMORY",
                confidence=0.90,
                evidence=["memory_usage"],
                reason="Memory usage remained consistently high.",
            )
        ]
    )

    workflow.case.set_recommendations(
        [build_recommendation()]
    )


def build_reasoning_summary(workflow):
    cycle_history = TechnicianRecoveryCycleHistory(workflow)
    return TechnicianReasoningSummary(
        workflow,
        cycle_history,
    )


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_summary(workflow):
    summary = TechnicianCaseSummary(workflow)
    summary.set_decision(build_decision(workflow))
    summary.set_notes(build_notes(workflow))
    summary.set_remediation_status("COMPLETED")
    summary.set_verification_status("VERIFIED")
    summary.set_escalation_status("NOT_ESCALATED")

    build_reasoning_data(workflow)

    summary.set_reasoning_summary(
        build_reasoning_summary(workflow)
    )

    return summary


def build_closure(workflow, technician="Test Technician"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason="Issue resolved and verified.",
    )


def finding_signature(finding):
    return (
        finding.finding_type,
        finding.category,
        finding.severity,
        finding.description,
    )


def correlation_signature(correlation):
    return (
        correlation.correlation_type,
        tuple(correlation.findings),
        correlation.strength,
        correlation.explanation,
    )


def root_cause_signature(root_cause):
    return (
        root_cause.cause,
        root_cause.category,
        root_cause.confidence,
        root_cause.reason,
    )


def recommendation_signature(recommendation):
    return (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )


def notes_snapshot(summary):
    return [
        (
            note.note_id,
            note.text,
            note.workflow_state,
        )
        for note in summary.notes
    ]


def reasoning_collections_snapshot(summary):
    return {
        "findings": [
            finding_signature(finding)
            for finding in summary.findings
        ],
        "correlations": [
            correlation_signature(correlation)
            for correlation in summary.workflow.case.correlations
        ],
        "root_causes": [
            root_cause_signature(root_cause)
            for root_cause in summary.root_causes
        ],
        "recommendations": [
            recommendation_signature(recommendation)
            for recommendation in summary.recommendations
        ],
    }


def summary_snapshot(summary):
    reasoning = summary.reasoning_summary

    return {
        "case_id": summary.case_id,
        "workflow_id": summary.workflow_id,
        "workflow_state": summary.workflow_state,
        "decision_id": summary.decision.decision_id,
        "decision_type": summary.decision.decision_type,
        "decision_notes": summary.decision.notes,
        "notes": notes_snapshot(summary),
        "remediation_status": summary.remediation_status,
        "verification_status": summary.verification_status,
        "escalation_status": summary.escalation_status,
        "reasoning_summary_identity": id(reasoning),
        "reasoning_overview": reasoning.overview,
        "reasoning_collections": reasoning_collections_snapshot(summary),
    }


def test_closure_does_not_change_complete_summary_snapshot():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    before = summary_snapshot(summary)

    summary.set_closure(build_closure(workflow))

    assert summary_snapshot(summary) == before


def test_closure_adds_only_closure_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    assert summary.closure is None

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.closure is closure
    assert summary.closure_id == closure.closure_id
    assert summary.closure_technician == closure.technician
    assert summary.closure_reason == closure.reason
    assert summary.closure_state == closure.workflow_state


def test_closure_does_not_change_decision():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    decision_before = summary.decision
    decision_id_before = summary.decision.decision_id

    summary.set_closure(build_closure(workflow))

    assert summary.decision is decision_before
    assert summary.decision.decision_id == decision_id_before


def test_closure_does_not_change_notes():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    notes_before = notes_snapshot(summary)

    summary.set_closure(build_closure(workflow))

    assert notes_snapshot(summary) == notes_before


def test_closure_does_not_change_operational_statuses():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    statuses_before = (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    )

    summary.set_closure(build_closure(workflow))

    assert (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    ) == statuses_before


def test_closure_does_not_change_reasoning_summary():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    reasoning_before = summary.reasoning_summary
    overview_before = reasoning_before.overview

    summary.set_closure(build_closure(workflow))

    assert summary.reasoning_summary is reasoning_before
    assert summary.reasoning_summary.overview == overview_before


def test_closure_does_not_change_diagnostic_reasoning_collections():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    reasoning_before = reasoning_collections_snapshot(summary)

    summary.set_closure(build_closure(workflow))

    assert reasoning_collections_snapshot(summary) == reasoning_before


def test_closure_does_not_change_case_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    case_id_before = summary.case_id
    workflow_id_before = summary.workflow_id

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    assert summary.case_id == case_id_before
    assert summary.workflow_id == workflow_id_before


def test_closure_does_not_change_workflow_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    state_before = summary.workflow_state

    summary.set_closure(build_closure(workflow))

    assert summary.workflow_state is state_before


def test_closure_does_not_change_workflow_history():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    history_before = list(summary.workflow_history)

    summary.set_closure(build_closure(workflow))

    assert summary.workflow_history == history_before


def test_closure_does_not_change_reasoning_after_reopen():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    summary.set_closure(build_closure(workflow))

    snapshot_before = summary_snapshot(summary)

    workflow.reopen()

    assert summary.reasoning_summary.overview == (
        snapshot_before["reasoning_overview"]
    )
    assert reasoning_collections_snapshot(summary) == (
        snapshot_before["reasoning_collections"]
    )


def test_closure_survives_reopen_without_becoming_workflow_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    workflow.reopen()

    assert summary.workflow_state.value == "INVESTIGATING"
    assert summary.closure is closure
    assert summary.closure_state.value == "RESOLVED"


def test_multiple_closures_preserve_complete_summary_state():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    first_closure = build_closure(workflow)
    summary.set_closure(first_closure)

    summary_before = summary_snapshot(summary)

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

    assert summary.case_id == summary_before["case_id"]
    assert summary.workflow_id == summary_before["workflow_id"]
    assert summary.decision.decision_id == (
        summary_before["decision_id"]
    )
    assert notes_snapshot(summary) == summary_before["notes"]
    assert (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    ) == (
        summary_before["remediation_status"],
        summary_before["verification_status"],
        summary_before["escalation_status"],
    )
    assert reasoning_collections_snapshot(summary) == (
        summary_before["reasoning_collections"]
    )


def test_closure_is_not_part_of_summary_reasoning():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert closure not in summary.findings
    assert closure not in summary.workflow.case.correlations
    assert closure not in summary.root_causes
    assert closure not in summary.recommendations
    assert closure not in summary.notes


def test_summary_components_remain_independent_of_closure_identity():
    workflow = build_workflow()
    summary = build_summary(workflow)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert summary.decision is not closure
    assert summary.reasoning_summary is not closure
    assert summary.notes[0] is not closure
    assert summary.findings[0] is not closure
    assert summary.workflow.case.correlations[0] is not closure
    assert summary.root_causes[0] is not closure
    assert summary.recommendations[0] is not closure