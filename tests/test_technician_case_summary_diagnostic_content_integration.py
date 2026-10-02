from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.root_cause import RootCauseCandidate
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_summary(workflow, history):
    summary = TechnicianCaseSummary(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    summary.set_reasoning_summary(reasoning_summary)

    return summary, reasoning_summary


def record_recovery_cycle(history, workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=history.cycle_count,
    )

    history.record_cycle(cycle)

    return cycle


def build_recommendation():
    return Recommendation(
        "test-recommendation",
        "Test recommendation",
        "MEDIUM",
        "Test recommendation description",
        "Test recommendation rationale",
    )


def build_root_cause():
    return RootCauseCandidate(
        cause="Test root cause",
        category="TEST",
        confidence=0.90,
        evidence=[],
        reason="Test root cause reason",
    )


def complete_lifecycle(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def continue_reinvestigation(workflow):
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_summary_exposes_existing_case_findings():
    workflow = build_workflow()

    finding = object()
    workflow.case.findings.append(finding)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    assert summary.findings == [finding]


def test_summary_exposes_existing_case_root_causes():
    workflow = build_workflow()

    root_cause = build_root_cause()
    workflow.case.root_causes.append(root_cause)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    assert summary.root_causes == [root_cause]


def test_summary_exposes_existing_case_recommendations():
    workflow = build_workflow()

    recommendation = build_recommendation()
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    assert summary.recommendations == [recommendation]


def test_summary_preserves_all_diagnostic_collections_together():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]


def test_recovery_cycle_does_not_appear_as_diagnostic_content():
    workflow = build_workflow()

    history = TechnicianRecoveryCycleHistory(workflow)
    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_diagnostic_content_does_not_replace_recovery_history():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert reasoning_summary.cycle_history.cycles[-1] is cycle
    assert reasoning_summary.cycle_history is history


def test_recovery_history_does_not_change_diagnostic_collections():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, reasoning_summary = build_summary(workflow, history)

    before_findings = summary.findings
    before_root_causes = summary.root_causes
    before_recommendations = summary.recommendations

    record_recovery_cycle(history, workflow)
    record_recovery_cycle(history, workflow)

    assert summary.findings == before_findings
    assert summary.root_causes == before_root_causes
    assert summary.recommendations == before_recommendations

    assert len(reasoning_summary.cycle_history.cycles) == 3


def test_diagnostic_content_survives_full_lifecycle():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    complete_lifecycle(workflow)

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_diagnostic_content_survives_reopen_and_reinvestigation():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)

    first_cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    complete_lifecycle(workflow)
    workflow.reopen()

    second_cycle = record_recovery_cycle(history, workflow)

    continue_reinvestigation(workflow)

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert reasoning_summary.cycle_history.cycles[-2:] == [
        first_cycle,
        second_cycle,
    ]


def test_diagnostic_content_survives_escalation():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    workflow.start_investigation()
    workflow.escalate()

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_summary_diagnostic_reads_are_snapshots():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    findings_snapshot = summary.findings
    root_causes_snapshot = summary.root_causes
    recommendations_snapshot = summary.recommendations

    findings_snapshot.clear()
    root_causes_snapshot.clear()
    recommendations_snapshot.clear()

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert workflow.case.findings == [finding]
    assert workflow.case.root_causes == [root_cause]
    assert workflow.case.recommendations == [recommendation]


def test_summary_reads_remain_consistent_after_case_updates():
    workflow = build_workflow()

    first_finding = object()
    first_root_cause = build_root_cause()
    first_recommendation = build_recommendation()

    workflow.case.findings.append(first_finding)
    workflow.case.root_causes.append(first_root_cause)
    workflow.case.recommendations.append(first_recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, _ = build_summary(workflow, history)

    assert summary.findings == [first_finding]
    assert summary.root_causes == [first_root_cause]
    assert summary.recommendations == [first_recommendation]

    second_finding = object()
    second_root_cause = build_root_cause()
    second_recommendation = build_recommendation()

    workflow.case.findings.append(second_finding)
    workflow.case.root_causes.append(second_root_cause)
    workflow.case.recommendations.append(second_recommendation)

    assert summary.findings == [
        first_finding,
        second_finding,
    ]

    assert summary.root_causes == [
        first_root_cause,
        second_root_cause,
    ]

    assert summary.recommendations == [
        first_recommendation,
        second_recommendation,
    ]


def test_summary_keeps_diagnostic_and_operational_surfaces_separate():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    cycle = record_recovery_cycle(history, workflow)

    summary, reasoning_summary = build_summary(workflow, history)

    workflow.start_investigation()

    assert summary.workflow_state == workflow.state

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert cycle not in summary.findings
    assert cycle not in summary.root_causes
    assert cycle not in summary.recommendations

    assert reasoning_summary.cycle_history.cycles[-1] is cycle


def test_repeated_summary_reads_do_not_create_or_duplicate_diagnostic_content():
    workflow = build_workflow()

    finding = object()
    root_cause = build_root_cause()
    recommendation = build_recommendation()

    workflow.case.findings.append(finding)
    workflow.case.root_causes.append(root_cause)
    workflow.case.recommendations.append(recommendation)

    history = TechnicianRecoveryCycleHistory(workflow)
    summary, reasoning_summary = build_summary(workflow, history)

    record_recovery_cycle(history, workflow)

    for _ in range(10):
        assert summary.findings == [finding]
        assert summary.root_causes == [root_cause]
        assert summary.recommendations == [recommendation]

        assert len(reasoning_summary.cycle_history.cycles) == 2

    assert workflow.case.findings == [finding]
    assert workflow.case.root_causes == [root_cause]
    assert workflow.case.recommendations == [recommendation]


def test_long_sequence_preserves_complete_summary_surface():
    workflow = build_workflow()

    findings = [object(), object(), object()]
    root_causes = [
        build_root_cause(),
        build_root_cause(),
    ]
    recommendations = [
        build_recommendation(),
        build_recommendation(),
        build_recommendation(),
    ]

    workflow.case.findings.extend(findings)
    workflow.case.root_causes.extend(root_causes)
    workflow.case.recommendations.extend(recommendations)

    history = TechnicianRecoveryCycleHistory(workflow)

    cycles = [
        record_recovery_cycle(history, workflow)
        for _ in range(5)
    ]

    summary, reasoning_summary = build_summary(workflow, history)

    complete_lifecycle(workflow)

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id

    assert summary.workflow_state == workflow.state
    assert summary.is_terminal is True

    assert summary.findings == findings
    assert summary.root_causes == root_causes
    assert summary.recommendations == recommendations

    assert reasoning_summary.cycle_history is history
    assert reasoning_summary.cycle_history.cycles[-5:] == cycles
    assert len(reasoning_summary.cycle_history.cycles) == 6