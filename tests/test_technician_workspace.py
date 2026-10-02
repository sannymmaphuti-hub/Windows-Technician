import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.technician_workspace import TechnicianWorkspace


def test_workspace_requires_technician_workflow():
    with pytest.raises(ValueError):
        TechnicianWorkspace(None)


def test_workspace_exposes_workflow_and_case():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.workflow is workflow
    assert workspace.case is case


def test_workspace_exposes_current_workflow_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.state == WorkflowState.OPEN

    workflow.start_investigation()

    assert workspace.state == WorkflowState.INVESTIGATING


def test_workspace_exposes_case_findings():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.findings == case.findings


def test_workspace_exposes_case_root_causes():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.root_causes == case.root_causes


def test_workspace_exposes_case_recommendations():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.recommendations == case.recommendations


def test_workspace_exposes_workflow_history():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workspace.history == [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
    ]


def test_workspace_reflects_terminal_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    workflow.start_investigation()
    workflow.escalate()

    assert workspace.state == WorkflowState.ESCALATED
    assert workspace.is_terminal is True


def test_workspace_does_not_mutate_case():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    original_findings = list(case.findings)
    original_root_causes = list(case.root_causes)
    original_recommendations = list(case.recommendations)

    _ = workspace.findings
    _ = workspace.root_causes
    _ = workspace.recommendations

    assert case.findings == original_findings
    assert case.root_causes == original_root_causes
    assert case.recommendations == original_recommendations


def test_workspace_does_not_execute_remediation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert not hasattr(workspace, "execute_remediation")


def test_workspace_is_read_only_for_case_collections():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    findings = workspace.findings
    recommendations = workspace.recommendations
    root_causes = workspace.root_causes

    findings.clear()
    recommendations.clear()
    root_causes.clear()

    assert case.findings == []
    assert case.recommendations == []
    assert case.root_causes == []


def test_workspace_exposes_case_id():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.case_id == case.case_id