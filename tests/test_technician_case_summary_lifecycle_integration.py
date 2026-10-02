from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.root_cause import RootCauseCandidate
from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def add_finding(workflow):
    finding = Finding(
        "MEMORY_PRESSURE",
        "MEMORY",
        "HIGH",
        "High memory usage detected.",
    )
    workflow.case.findings.append(finding)
    return finding


def add_root_cause(workflow):
    root_cause = RootCauseCandidate(
        cause="Insufficient available memory",
        category="MEMORY",
        confidence=0.90,
        evidence=[],
        reason="Memory pressure is supported by diagnostic evidence.",
    )
    workflow.case.root_causes.append(root_cause)
    return root_cause


def add_recommendation(workflow):
    recommendation = Recommendation(
        "memory-review",
        "Review memory usage",
        "MEDIUM",
        "Review applications consuming significant memory.",
        "Reducing unnecessary memory pressure may improve responsiveness.",
    )
    workflow.case.recommendations.append(recommendation)
    return recommendation


def advance_to_investigating(workflow):
    workflow.start_investigation()


def advance_to_diagnosed(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    workflow.mark_diagnosed()


def advance_to_action_required(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    if workflow.state.name == "INVESTIGATING":
        workflow.mark_diagnosed()

    workflow.require_action()


def advance_to_remediating(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    if workflow.state.name == "INVESTIGATING":
        workflow.mark_diagnosed()

    if workflow.state.name == "DIAGNOSED":
        workflow.require_action()

    workflow.start_remediation()


def advance_to_verifying(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    if workflow.state.name == "INVESTIGATING":
        workflow.mark_diagnosed()

    if workflow.state.name == "DIAGNOSED":
        workflow.require_action()

    if workflow.state.name == "ACTION_REQUIRED":
        workflow.start_remediation()

    workflow.start_verification()


def advance_to_resolved(workflow):
    if workflow.state.name == "OPEN":
        workflow.start_investigation()

    if workflow.state.name == "INVESTIGATING":
        workflow.mark_diagnosed()

    if workflow.state.name == "DIAGNOSED":
        workflow.require_action()

    if workflow.state.name == "ACTION_REQUIRED":
        workflow.start_remediation()

    if workflow.state.name == "REMEDIATING":
        workflow.start_verification()

    workflow.resolve()


def test_summary_is_available_in_open_state():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert workflow.state.name == "OPEN"
    assert summary.workflow is workflow
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_summary_tracks_investigating_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()

    assert workflow.state.name == "INVESTIGATING"
    assert summary.workflow is workflow


def test_summary_tracks_diagnosed_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_diagnosed(workflow)

    assert workflow.state.name == "DIAGNOSED"
    assert summary.workflow is workflow


def test_summary_tracks_action_required_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_action_required(workflow)

    assert workflow.state.name == "ACTION_REQUIRED"
    assert summary.workflow is workflow


def test_summary_tracks_remediating_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_remediating(workflow)

    assert workflow.state.name == "REMEDIATING"
    assert summary.workflow is workflow


def test_summary_tracks_verifying_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_verifying(workflow)

    assert workflow.state.name == "VERIFYING"
    assert summary.workflow is workflow


def test_summary_tracks_resolved_state():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_resolved(workflow)

    assert workflow.state.name == "RESOLVED"
    assert summary.workflow is workflow


def test_diagnostic_surfaces_survive_full_lifecycle():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    advance_to_resolved(workflow)

    assert workflow.state.name == "RESOLVED"

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert summary.findings[0] is finding
    assert summary.root_causes[0] is root_cause
    assert summary.recommendations[0] is recommendation


def test_summary_created_before_lifecycle_progress_remains_valid_after_resolution():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    advance_to_resolved(workflow)

    assert workflow.state.name == "RESOLVED"
    assert summary.workflow is workflow
    assert summary.findings == []
    assert summary.root_causes == []
    assert summary.recommendations == []


def test_summary_created_mid_lifecycle_remains_valid_after_resolution():
    workflow = build_workflow()

    advance_to_action_required(workflow)

    summary = TechnicianCaseSummary(workflow)

    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state.name == "RESOLVED"

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_summary_reflects_diagnostics_added_during_lifecycle():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()

    finding = add_finding(workflow)

    workflow.mark_diagnosed()

    root_cause = add_root_cause(workflow)

    workflow.require_action()

    recommendation = add_recommendation(workflow)

    assert workflow.state.name == "ACTION_REQUIRED"

    assert summary.findings[0] is finding
    assert summary.root_causes[0] is root_cause
    assert summary.recommendations[0] is recommendation


def test_summary_does_not_change_workflow_state():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    _ = summary.findings
    _ = summary.root_causes
    _ = summary.recommendations
    _ = summary.notes
    _ = summary.reasoning_summary
    _ = summary.decision

    assert workflow.state.name == "OPEN"


def test_repeated_summary_reads_do_not_advance_lifecycle():
    workflow = build_workflow()
    summary = TechnicianCaseSummary(workflow)

    for _ in range(20):
        _ = summary.workflow
        _ = summary.findings
        _ = summary.root_causes
        _ = summary.recommendations
        _ = summary.notes
        _ = summary.reasoning_summary
        _ = summary.decision

    assert workflow.state.name == "OPEN"


def test_summary_survives_reopen_from_resolved_state():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    advance_to_resolved(workflow)

    assert workflow.state.name == "RESOLVED"

    workflow.reopen()

    assert workflow.state.name == "INVESTIGATING"

    assert summary.workflow is workflow
    assert summary.findings[0] is finding
    assert summary.root_causes[0] is root_cause
    assert summary.recommendations[0] is recommendation


def test_summary_reflects_new_diagnostics_after_reopen():
    workflow = build_workflow()

    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    advance_to_resolved(workflow)

    workflow.reopen()

    new_finding = Finding(
        "PROCESS_PRESSURE",
        "PROCESS",
        "MEDIUM",
        "A process is consuming elevated resources.",
    )
    workflow.case.findings.append(new_finding)

    assert workflow.state.name == "INVESTIGATING"
    assert len(summary.findings) == 2
    assert summary.findings[1] is new_finding


def test_two_summaries_remain_consistent_across_lifecycle():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    first_summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()

    second_summary = TechnicianCaseSummary(workflow)

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state.name == "RESOLVED"

    assert first_summary.workflow is workflow
    assert second_summary.workflow is workflow

    assert first_summary.findings[0] is finding
    assert second_summary.findings[0] is finding

    assert first_summary.root_causes[0] is root_cause
    assert second_summary.root_causes[0] is root_cause

    assert first_summary.recommendations[0] is recommendation
    assert second_summary.recommendations[0] is recommendation


def test_summary_remains_read_only_with_respect_to_lifecycle():
    workflow = build_workflow()

    summary = TechnicianCaseSummary(workflow)

    assert workflow.state.name == "OPEN"

    summary.findings.clear()
    summary.root_causes.clear()
    summary.recommendations.clear()

    assert workflow.state.name == "OPEN"

    workflow.start_investigation()

    assert workflow.state.name == "INVESTIGATING"

    summary.findings.clear()
    summary.root_causes.clear()
    summary.recommendations.clear()

    assert workflow.state.name == "INVESTIGATING"


def test_full_lifecycle_preserves_workflow_identity_and_domain_identity():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state.name == "RESOLVED"

    assert summary.workflow is workflow
    assert summary.findings[0] is finding
    assert summary.root_causes[0] is root_cause
    assert summary.recommendations[0] is recommendation