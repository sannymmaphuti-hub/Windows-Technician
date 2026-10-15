from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)
from engine.system_wide_intelligence_projection import (
    SystemWideIntelligenceProjection,
)
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_workspace import TechnicianWorkspace


def make_workspace():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return workflow, case


def test_workspace_accepts_system_wide_intelligence_projection():
    workflow, case = make_workspace()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    workspace = TechnicianWorkspace(
        workflow,
        intelligence_projection=projection,
    )

    assert workspace.intelligence_projection is projection


def test_workspace_rejects_invalid_intelligence_projection():
    workflow, _ = make_workspace()

    try:
        TechnicianWorkspace(
            workflow,
            intelligence_projection=object(),
        )
    except ValueError as exc:
        assert "SystemWideIntelligenceProjection" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_workspace_intelligence_snapshot_is_empty_when_unbound():
    workflow, _ = make_workspace()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.intelligence_snapshot() == {}


def test_workspace_exposes_intelligence_projection():
    workflow, case = make_workspace()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    workspace = TechnicianWorkspace(
        workflow,
        intelligence_projection=projection,
    )

    snapshot = workspace.intelligence_snapshot()

    assert set(snapshot) == {
        "case",
        "intelligence",
    }

    assert snapshot["case"]["case_id"] == case.case_id


def test_workspace_intelligence_snapshot_is_defensive():
    workflow, case = make_workspace()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    workspace = TechnicianWorkspace(
        workflow,
        intelligence_projection=projection,
    )

    snapshot = workspace.intelligence_snapshot()
    snapshot["intelligence"]["investigation"]["tampered"] = True

    assert "tampered" not in workspace.intelligence_snapshot()[
        "intelligence"
    ]["investigation"]


def test_workspace_can_bind_intelligence_projection():
    workflow, case = make_workspace()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    workspace = TechnicianWorkspace(workflow)

    workspace.bind_intelligence_projection(projection)

    assert workspace.intelligence_projection is projection


def test_workspace_can_clear_intelligence_projection():
    workflow, case = make_workspace()

    integration = SystemWideIntelligenceIntegration(case)
    projection = SystemWideIntelligenceProjection(integration)

    workspace = TechnicianWorkspace(
        workflow,
        intelligence_projection=projection,
    )

    workspace.clear_intelligence_projection()

    assert workspace.intelligence_projection is None
    assert workspace.intelligence_snapshot() == {}


def test_workspace_does_not_gain_intelligence_processing_methods():
    workflow, _ = make_workspace()

    workspace = TechnicianWorkspace(workflow)

    forbidden = {
        "investigate",
        "analyze",
        "analyze_relationships",
        "analyze_root_causes",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(workspace)))
