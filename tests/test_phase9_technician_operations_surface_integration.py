from engine.managed_machine import ManagedMachine
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.technician_workspace import TechnicianWorkspace
from engine.case_timeline import CaseTimeline
from engine.case_queue import CaseQueue
from engine.machine_overview import MachineOverview
from engine.technician_dashboard import TechnicianDashboard
from engine.case_reporting import CaseReporting


def create_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="TEST-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def create_case(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    return case


def create_workflow():
    machine = create_machine()
    case = create_case(machine)
    workflow = TechnicianWorkflow(case)
    return machine, case, workflow


def progress_to_diagnosed(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()


def progress_to_action_required(workflow):
    progress_to_diagnosed(workflow)
    workflow.require_action()


def progress_to_verification(workflow):
    progress_to_action_required(workflow)
    workflow.start_remediation()
    workflow.start_verification()


# ============================================================
# SHARED CASE / WORKFLOW IDENTITY
# ============================================================


def test_all_operations_surfaces_reference_same_case():
    _, case, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.case is case
    assert timeline.case is case
    assert reporting.case is case


def test_all_operations_surfaces_preserve_case_id():
    _, case, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.case_id == case.case_id
    assert timeline.case_id == case.case_id
    assert reporting.case_id == case.case_id


def test_all_operations_surfaces_preserve_machine_identity():
    machine, case, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.machine_id == machine.machine_id
    assert timeline.machine_id == machine.machine_id
    assert reporting.machine_id == machine.machine_id

    assert workspace.hostname == machine.hostname
    assert timeline.hostname == machine.hostname
    assert reporting.hostname == machine.hostname


# ============================================================
# WORKSPACE INTEGRATION
# ============================================================


def test_workspace_reflects_open_workflow():
    _, _, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.OPEN
    assert workspace.is_terminal is False


def test_workspace_reflects_investigating_state():
    _, _, workflow = create_workflow()

    workflow.start_investigation()
    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.INVESTIGATING


def test_workspace_reflects_diagnosed_state():
    _, _, workflow = create_workflow()

    progress_to_diagnosed(workflow)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.DIAGNOSED


def test_workspace_reflects_action_required_state():
    _, _, workflow = create_workflow()

    progress_to_action_required(workflow)
    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.ACTION_REQUIRED


def test_workspace_reflects_active_remediation_state():
    _, _, workflow = create_workflow()

    progress_to_action_required(workflow)
    workflow.start_remediation()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.REMEDIATING


def test_workspace_reflects_verifying_state():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)

    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.VERIFYING


def test_workspace_reflects_resolved_state():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    workspace = TechnicianWorkspace(workflow)

    assert workspace.state is WorkflowState.RESOLVED
    assert workspace.is_terminal is True


# ============================================================
# CASE TIMELINE INTEGRATION
# ============================================================


def test_timeline_reflects_workflow_state():
    _, _, workflow = create_workflow()

    workflow.start_investigation()

    timeline = CaseTimeline(workflow)

    assert timeline.state is WorkflowState.INVESTIGATING


def test_timeline_preserves_workflow_history():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)

    timeline = CaseTimeline(workflow)

    assert timeline.history == workflow.history
    assert len(timeline.history) == 5


def test_timeline_reflects_terminal_state():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    timeline = CaseTimeline(workflow)

    assert timeline.state is WorkflowState.RESOLVED
    assert timeline.is_terminal is True


# ============================================================
# CASE QUEUE INTEGRATION
# ============================================================


def test_case_queue_accepts_existing_case():
    _, case, _ = create_workflow()

    queue = CaseQueue()

    queue.add_case(case)

    assert queue.case_count == 1
    assert case in queue.open_cases


def test_case_queue_tracks_case_by_machine():
    machine, case, _ = create_workflow()

    queue = CaseQueue()
    queue.add_case(case)

    machine_cases = queue.for_machine(machine.machine_id)

    assert case in machine_cases
    assert len(machine_cases) == 1


def test_case_queue_open_cases_remain_available_after_workflow_progression():
    _, case, workflow = create_workflow()

    queue = CaseQueue()
    queue.add_case(case)

    progress_to_diagnosed(workflow)

    assert case in queue.open_cases


# ============================================================
# MACHINE OVERVIEW INTEGRATION
# ============================================================


def test_machine_overview_accepts_same_machine_case():
    machine, case, _ = create_workflow()

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert case in overview.cases


def test_machine_overview_preserves_machine_identity():
    machine, _, _ = create_workflow()

    overview = MachineOverview(machine)

    assert overview.machine_id == machine.machine_id
    assert overview.hostname == machine.hostname


def test_machine_overview_tracks_case_count():
    machine, case, _ = create_workflow()

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert len(overview.cases) == 1


# ============================================================
# DASHBOARD INTEGRATION
# ============================================================


def test_dashboard_accepts_managed_machine():
    machine = create_machine()

    dashboard = TechnicianDashboard()
    dashboard.add_machine(machine)

    assert machine in dashboard.machines


def test_dashboard_accepts_case():
    _, case, _ = create_workflow()

    dashboard = TechnicianDashboard()
    dashboard.add_case(case)

    assert case in dashboard.cases


def test_dashboard_case_count_reflects_added_case():
    _, case, _ = create_workflow()

    dashboard = TechnicianDashboard()
    dashboard.add_case(case)

    assert dashboard.case_count == 1


# ============================================================
# REPORTING INTEGRATION
# ============================================================


def test_reporting_reflects_current_workflow_state():
    _, _, workflow = create_workflow()

    progress_to_diagnosed(workflow)

    reporting = CaseReporting(workflow)

    assert reporting.state is WorkflowState.DIAGNOSED


def test_reporting_preserves_history():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)

    reporting = CaseReporting(workflow)

    assert reporting.history == workflow.history
    assert len(reporting.history) == 5


def test_reporting_reflects_terminal_workflow_state():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    reporting = CaseReporting(workflow)

    assert reporting.state is WorkflowState.RESOLVED


# ============================================================
# CROSS-SURFACE CONSISTENCY
# ============================================================


def test_workspace_timeline_and_reporting_reflect_same_current_state():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.state is WorkflowState.VERIFYING
    assert timeline.state is WorkflowState.VERIFYING
    assert reporting.state is WorkflowState.VERIFYING


def test_workspace_timeline_and_reporting_reflect_resolution():
    _, _, workflow = create_workflow()

    progress_to_verification(workflow)
    workflow.resolve()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.state is WorkflowState.RESOLVED
    assert timeline.state is WorkflowState.RESOLVED
    assert reporting.state is WorkflowState.RESOLVED

    assert workspace.is_terminal is True
    assert timeline.is_terminal is True


def test_case_identity_remains_consistent_across_operations_layer():
    _, case, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert {
        workspace.case_id,
        timeline.case_id,
        reporting.case_id,
    } == {case.case_id}


def test_machine_identity_remains_consistent_across_operations_layer():
    machine, _, workflow = create_workflow()

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert {
        workspace.machine_id,
        timeline.machine_id,
        reporting.machine_id,
    } == {machine.machine_id}