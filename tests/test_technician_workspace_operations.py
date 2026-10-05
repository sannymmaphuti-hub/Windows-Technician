# ==========================================
# Windows Technician v0.8
# TECHNICIAN WORKSPACE OPERATIONS TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_workspace import TechnicianWorkspace


def build_case():
    case = DiagnosticCase()
    case.machine_id = "machine-001"
    case.hostname = "TECH-PC"
    return case


def build_workflow():
    return TechnicianWorkflow(build_case())


def test_technician_workspace_exists():
    workspace = TechnicianWorkspace(build_workflow())

    assert workspace is not None


def test_workspace_preserves_workflow_identity():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.workflow is workflow


def test_workspace_exposes_case():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is workflow.case


def test_workspace_exposes_case_id():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case_id == workflow.case.case_id


def test_workspace_exposes_workflow_state():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.state == workflow.state


def test_workspace_exposes_terminal_state():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.is_terminal == workflow.is_terminal


def test_workspace_exposes_history():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.history == workflow.history


def test_workspace_exposes_findings():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.findings == workflow.case.findings


def test_workspace_exposes_root_causes():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.root_causes == workflow.case.root_causes


def test_workspace_exposes_recommendations():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.recommendations == (
        workflow.case.recommendations
    )


def test_workspace_exposes_machine_id():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.machine_id == "machine-001"


def test_workspace_exposes_hostname():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.hostname == "TECH-PC"


def test_workspace_rejects_invalid_workflow():
    try:
        TechnicianWorkspace(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid workflow should raise ValueError."
        )


def test_workspace_does_not_create_second_case():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is workflow.case


def test_workspace_does_not_diagnose():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert not hasattr(workspace, "diagnose")
    assert not hasattr(workspace, "diagnostic_pipeline")


def test_workspace_does_not_authorize():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert not hasattr(workspace, "authorize")
    assert not hasattr(workspace, "authorization_status")


def test_workspace_does_not_execute():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert not hasattr(workspace, "execute")
    assert not hasattr(workspace, "execution_status")


def test_workspace_does_not_remediate():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert not hasattr(workspace, "remediate")
    assert not hasattr(workspace, "remediation_action")
    assert not hasattr(workspace, "remediation_actions")


def test_workspace_does_not_bypass_workflow():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.workflow is workflow
    assert workspace.state == workflow.state


def test_workspace_is_read_oriented():
    workflow = build_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is workflow.case
    assert workspace.workflow is workflow