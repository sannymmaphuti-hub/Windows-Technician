import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_workspace import TechnicianWorkspace
from engine.technician_workflow import TechnicianWorkflow


def build_workspace():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return TechnicianWorkspace(workflow), workflow, case


def test_workspace_creates_canonical_case_summary():
    workspace, workflow, _ = build_workspace()

    assert isinstance(workspace.case_summary, TechnicianCaseSummary)
    assert workspace.case_summary.workflow is workflow


def test_workspace_accepts_matching_case_summary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    summary = TechnicianCaseSummary(workflow)

    workspace = TechnicianWorkspace(
        workflow,
        case_summary=summary,
    )

    assert workspace.case_summary is summary


def test_workspace_rejects_case_summary_for_different_workflow():
    case_a = DiagnosticCase()
    workflow_a = TechnicianWorkflow(case_a)

    case_b = DiagnosticCase()
    workflow_b = TechnicianWorkflow(case_b)
    summary_b = TechnicianCaseSummary(workflow_b)

    with pytest.raises(ValueError, match="different workflow"):
        TechnicianWorkspace(
            workflow_a,
            case_summary=summary_b,
        )


def test_workspace_exposes_operational_case_status():
    workspace, _, _ = build_workspace()

    workspace.case_summary.set_decision("REMEDIATE")
    workspace.case_summary.set_remediation_status("AUTHORIZED")
    workspace.case_summary.set_verification_status("PENDING")
    workspace.case_summary.set_escalation_status("NOT_ESCALATED")

    assert workspace.decision == "REMEDIATE"
    assert workspace.remediation_status == "AUTHORIZED"
    assert workspace.verification_status == "PENDING"
    assert workspace.escalation_status == "NOT_ESCALATED"


def test_workspace_case_projection_contains_complete_surface():
    workspace, workflow, case = build_workspace()

    workspace.case_summary.set_decision("REMEDIATE")
    workspace.case_summary.set_remediation_status("AUTHORIZED")
    workspace.case_summary.set_verification_status("PENDING")
    workspace.case_summary.set_escalation_status("NOT_ESCALATED")

    projection = workspace.case_projection()

    assert set(projection) == {
        "case",
        "findings",
        "root_causes",
        "recommendations",
        "decision",
        "notes",
        "remediation_status",
        "verification_status",
        "escalation_status",
        "history",
        "closure",
        "reasoning_summary",
    }

    assert projection["case"] == {
        "case_id": case.case_id,
        "state": workflow.state,
        "is_terminal": workflow.is_terminal,
    }

    assert projection["decision"] == "REMEDIATE"
    assert projection["remediation_status"] == "AUTHORIZED"
    assert projection["verification_status"] == "PENDING"
    assert projection["escalation_status"] == "NOT_ESCALATED"


def test_workspace_case_projection_is_defensive():
    workspace, _, case = build_workspace()

    case.findings.append({"id": "finding-1"})

    projection = workspace.case_projection()
    projection["findings"].append({"id": "finding-2"})

    assert workspace.findings == [{"id": "finding-1"}]


def test_workspace_projection_tracks_workflow_state():
    workspace, workflow, _ = build_workspace()

    workflow.start_investigation()

    projection = workspace.case_projection()

    assert projection["case"]["state"] == workflow.state
    assert projection["case"]["is_terminal"] is False
    assert projection["history"] == workspace.history


def test_workspace_has_no_remediation_execution_surface():
    workspace, _, _ = build_workspace()

    assert not hasattr(workspace, "execute_remediation")
    assert not hasattr(workspace, "verify_remediation")
    assert not hasattr(workspace, "authorize_remediation")

def test_workspace_rejects_invalid_authorization():
    workspace, workflow, case = build_workspace()

    try:
        workspace.__class__(
            workflow,
            case_summary=workspace.case_summary,
            authorization="AUTHORIZED",
        )
    except ValueError:
        return

    raise AssertionError(
        "TechnicianWorkspace must reject non-RemediationAuthorization values."
    )


def test_workspace_actions_keep_decision_separate_from_authorization():
    from packaging.remediation_authorization import (
        AuthorizationReason,
        AuthorizationState,
        RemediationAuthorization,
    )

    workspace, workflow, case = build_workspace()

    workspace.case_summary.set_decision("REMEDIATE")

    authorization = RemediationAuthorization(
        action_id="action-001",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    workspace = workspace.__class__(
        workflow,
        case_summary=workspace.case_summary,
        authorization=authorization,
    )

    case.recommendations.append("memory_review")

    actions = workspace.technician_actions()

    assert len(actions) == 1
    assert actions[0]["decision"] == "REMEDIATE"
    assert actions[0]["authorization"] == {
        "state": "AUTHORIZED",
        "reason": "TECHNICIAN_APPROVED",
        "action_id": "action-001",
    }


def test_workspace_without_authorization_is_safe_by_default():
    workspace, workflow, case = build_workspace()

    case.recommendations.append("memory_review")

    actions = workspace.technician_actions()

    assert actions[0]["authorization"] == {
        "state": "UNAUTHORIZED",
        "reason": "NOT_REQUESTED",
        "action_id": None,
    }
