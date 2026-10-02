from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_reasoning_summary import (
    TechnicianReasoningSummary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    return summary, workflow


def test_summary_tracks_open_workflow():
    summary, workflow = create_summary()

    assert summary.workflow is workflow


def test_summary_tracks_investigating_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()

    assert summary.workflow is workflow


def test_summary_tracks_diagnosed_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert summary.workflow is workflow


def test_summary_tracks_action_required_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert summary.workflow is workflow


def test_summary_tracks_remediating_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    assert summary.workflow is workflow


def test_summary_tracks_verifying_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    assert summary.workflow is workflow


def test_summary_tracks_resolved_workflow():
    summary, workflow = create_summary()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.workflow is workflow