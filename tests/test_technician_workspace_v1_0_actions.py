from engine.diagnostic_case import DiagnosticCase
from engine.technician_workspace import TechnicianWorkspace
from engine.technician_workflow import TechnicianWorkflow
from packaging.remediation_authorization import (
    AuthorizationReason,
    AuthorizationState,
    RemediationAuthorization,
)


def build_workspace():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return TechnicianWorkspace(workflow), case


def test_workspace_has_no_actions_without_recommendations():
    workspace, _ = build_workspace()

    assert workspace.technician_actions() == []


def test_workspace_action_surface_exposes_recommendation_state():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    actions = workspace.technician_actions()

    assert len(actions) == 1
    assert actions[0]["case_id"] == case.case_id
    assert actions[0]["recommendations"] == [
        {
            "action": "memory_review",
            "severity": "HIGH",
        }
    ]


def test_workspace_action_defaults_to_unauthorized():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    action = workspace.technician_actions()[0]

    assert action["authorization"] == {
        "state": AuthorizationState.UNAUTHORIZED.value,
        "reason": AuthorizationReason.NOT_REQUESTED.value,
        "action_id": None,
    }


def test_workspace_projects_explicit_authorization():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    authorization = RemediationAuthorization(
        action_id="action-001",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.TECHNICIAN_APPROVED,
    )

    workspace.case_summary.set_decision(authorization)

    action = workspace.technician_actions()[0]

    assert action["authorization"] == {
        "state": "AUTHORIZED",
        "reason": "TECHNICIAN_APPROVED",
        "action_id": "action-001",
    }


def test_workspace_projects_denied_authorization():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    authorization = RemediationAuthorization(
        action_id="action-002",
        state=AuthorizationState.DENIED,
        reason=AuthorizationReason.TECHNICIAN_DENIED,
    )

    workspace.case_summary.set_decision(authorization)

    action = workspace.technician_actions()[0]

    assert action["authorization"]["state"] == "DENIED"
    assert action["authorization"]["reason"] == "TECHNICIAN_DENIED"


def test_workspace_action_projection_is_defensive():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    actions = workspace.technician_actions()
    actions[0]["recommendations"][0]["severity"] = "LOW"

    assert case.recommendations[0]["severity"] == "HIGH"


def test_workspace_action_surface_never_executes_remediation():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    _ = workspace.technician_actions()

    assert workspace.remediation_status is None
    assert workspace.verification_status is None


def test_case_projection_contains_technician_actions():
    workspace, case = build_workspace()

    case.recommendations.append({
        "action": "memory_review",
        "severity": "HIGH",
    })

    projection = workspace.case_projection()

    assert "technician_actions" in projection
    assert len(projection["technician_actions"]) == 1
