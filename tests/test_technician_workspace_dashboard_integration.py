from engine.diagnostic_case import DiagnosticCase
from engine.technician_dashboard import TechnicianDashboard
from engine.technician_dashboard_presenter import TechnicianDashboardPresenter
from engine.dashboard_view_model import DashboardViewModel
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_workspace import TechnicianWorkspace


class ApplicationState:
    active_machine_id = "machine-001"
    active_case_id = "case-001"


def build_workspace():
    case = DiagnosticCase()
    case.machine_id = "machine-001"
    case.hostname = "TEST-PC"

    workflow = TechnicianWorkflow(case)
    return TechnicianWorkspace(workflow)


def build_presenter():
    dashboard = TechnicianDashboard()

    view_model = DashboardViewModel(
        ApplicationState(),
        {
            "health": {
                "status": "HEALTHY",
                "score": 95,
            },
            "active_cases": [
                {
                    "case_id": "case-001",
                    "machine_id": "machine-001",
                    "lifecycle_state": "INVESTIGATING",
                }
            ],
            "fleet_alerts": [],
            "unresolved_problems": [],
            "remediation_status": [],
            "verification_status": [],
            "recent_activity": [],
        },
    )

    view_model.bind_dashboard(dashboard)
    return TechnicianDashboardPresenter(view_model)


def test_workspace_preserves_existing_workflow_surface():
    workspace = build_workspace()

    assert workspace.case_id == workspace.case.case_id
    assert workspace.state == workspace.workflow.state
    assert workspace.is_terminal == workspace.workflow.is_terminal
    assert workspace.history == workspace.workflow.history
    assert workspace.findings == list(workspace.case.findings)
    assert workspace.root_causes == list(workspace.case.root_causes)
    assert workspace.recommendations == list(workspace.case.recommendations)
    assert workspace.machine_id == workspace.case.machine_id
    assert workspace.hostname == workspace.case.hostname


def test_workspace_can_bind_dashboard_presenter():
    workspace = build_workspace()
    presenter = build_presenter()

    workspace.bind_dashboard_presenter(presenter)

    assert workspace.dashboard_presenter is presenter


def test_workspace_dashboard_snapshot_delegates_to_presenter():
    workspace = build_workspace()
    presenter = build_presenter()

    workspace.bind_dashboard_presenter(presenter)

    snapshot = workspace.dashboard_snapshot()

    assert isinstance(snapshot, dict)
    assert set(snapshot) == {
        "health",
        "active_cases",
        "fleet_alerts",
        "unresolved_problems",
        "remediation_status",
        "verification_status",
        "recent_activity",
    }


def test_workspace_dashboard_snapshot_is_defensive():
    workspace = build_workspace()
    presenter = build_presenter()

    workspace.bind_dashboard_presenter(presenter)

    first = workspace.dashboard_snapshot()
    first["health"]["status"] = "CORRUPTED"

    second = workspace.dashboard_snapshot()

    assert second["health"]["status"] != "CORRUPTED"


def test_workspace_can_clear_dashboard_presenter():
    workspace = build_workspace()
    presenter = build_presenter()

    workspace.bind_dashboard_presenter(presenter)
    workspace.clear_dashboard_presenter()

    assert workspace.dashboard_presenter is None
    assert workspace.dashboard_snapshot() == {}


def test_workspace_rejects_invalid_dashboard_presenter():
    workspace = build_workspace()

    try:
        workspace.bind_dashboard_presenter(object())
    except ValueError as exc:
        assert "TechnicianDashboardPresenter" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_workspace_remains_presentation_only():
    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    workspace_methods = {
        name
        for name in dir(TechnicianWorkspace)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(workspace_methods)
