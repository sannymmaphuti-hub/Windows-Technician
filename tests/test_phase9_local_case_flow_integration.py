from engine.case_handoff import CaseHandoff
from engine.case_queue import CaseQueue
from engine.case_reporting import CaseReporting
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.machine_overview import MachineOverview
from engine.technician_dashboard import TechnicianDashboard
from engine.technician_notes import TechnicianNotes
from engine.technician_workflow import TechnicianWorkflow
from engine.technician_workspace import TechnicianWorkspace


def create_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="TEST-PC",
        platform="Windows",
        operating_system="Windows 10",
    )


def create_case(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    return case


def create_workflow(case):
    return TechnicianWorkflow(case)


def test_local_case_can_enter_shared_case_architecture():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert workflow.case is case
    assert workflow.case.machine_id == machine.machine_id


def test_dashboard_can_surface_the_same_machine_and_case():
    machine = create_machine()
    case = create_case(machine)

    dashboard = TechnicianDashboard()

    dashboard.add_machine(machine)
    dashboard.add_case(case)

    assert dashboard.machine_count == 1
    assert dashboard.case_count == 1
    assert dashboard.machines[0] is machine
    assert dashboard.cases[0] is case


def test_machine_overview_can_surface_the_same_case():
    machine = create_machine()
    case = create_case(machine)

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert overview.machine_id == machine.machine_id
    assert overview.hostname == machine.hostname
    assert overview.cases[0] is case
    assert overview.case_count == 1


def test_case_queue_can_surface_the_same_case():
    machine = create_machine()
    case = create_case(machine)

    queue = CaseQueue()
    queue.add_case(case)

    assert queue.case_count == 1
    assert queue.for_machine(machine.machine_id) == [case]
    assert case in queue.open_cases
    assert case in queue.active_cases


def test_workspace_reuses_the_existing_workflow_and_case():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    workspace = TechnicianWorkspace(workflow)

    assert workspace.case is case
    assert workspace.case_id == case.case_id
    assert workspace.machine_id == machine.machine_id
    assert workspace.hostname == machine.hostname
    assert workspace.state == workflow.state


def test_timeline_reuses_workflow_history():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    timeline = CaseTimeline(workflow)

    assert timeline.case is case
    assert timeline.case_id == case.case_id
    assert timeline.machine_id == machine.machine_id
    assert timeline.hostname == machine.hostname
    assert timeline.history == workflow.history
    assert timeline.state == workflow.state
    assert timeline.is_terminal == workflow.is_terminal


def test_notes_attach_to_the_same_case_without_replacing_it():
    machine = create_machine()
    case = create_case(machine)

    notes = TechnicianNotes(case)
    notes.add_note("Initial technician observation.")

    assert notes.case_id == case.case_id
    assert notes.note_count == 1
    assert notes.notes == ["Initial technician observation."]
    assert notes.case is case


def test_handoff_reuses_the_existing_workflow():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Requires additional investigation.",
    )

    assert handoff.workflow is workflow
    assert handoff.case is case
    assert handoff.case_id == case.case_id
    assert handoff.machine_id == machine.machine_id
    assert handoff.hostname == machine.hostname
    assert handoff.status == "PENDING"


def test_reporting_reuses_the_existing_workflow_and_case():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    reporting = CaseReporting(workflow)

    assert reporting.workflow is workflow
    assert reporting.case is case
    assert reporting.case_id == case.case_id
    assert reporting.machine_id == machine.machine_id
    assert reporting.hostname == machine.hostname
    assert reporting.state == workflow.state


def test_reporting_exposes_case_evidence_surfaces_without_copying_the_case():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    case.findings.append("Finding A")
    case.root_causes.append("Root cause A")
    case.recommendations.append("Recommendation A")

    reporting = CaseReporting(workflow)

    assert reporting.findings == ["Finding A"]
    assert reporting.root_causes == ["Root cause A"]
    assert reporting.recommendations == ["Recommendation A"]
    assert reporting.case is case


def test_all_operations_surfaces_refer_to_the_same_case():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    overview = MachineOverview(machine)
    queue = CaseQueue()
    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    notes = TechnicianNotes(case)
    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Additional investigation required.",
    )
    reporting = CaseReporting(workflow)

    overview.add_case(case)
    queue.add_case(case)

    assert overview.cases[0] is case
    assert queue.cases[0] is case
    assert workspace.case is case
    assert timeline.case is case
    assert notes.case is case
    assert handoff.case is case
    assert reporting.case is case


def test_machine_identity_is_consistent_across_all_operations_surfaces():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    overview = MachineOverview(machine)
    queue = CaseQueue()
    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Additional investigation required.",
    )
    reporting = CaseReporting(workflow)

    overview.add_case(case)
    queue.add_case(case)

    assert overview.machine_id == machine.machine_id
    assert queue.for_machine(machine.machine_id) == [case]
    assert workspace.machine_id == machine.machine_id
    assert timeline.machine_id == machine.machine_id
    assert handoff.machine_id == machine.machine_id
    assert reporting.machine_id == machine.machine_id


def test_case_state_is_consistent_across_workflow_surfaces():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert workspace.state == workflow.state
    assert timeline.state == workflow.state
    assert reporting.state == workflow.state


def test_case_history_is_consistent_across_workflow_surfaces():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    timeline = CaseTimeline(workflow)
    reporting = CaseReporting(workflow)

    assert timeline.history == workflow.history
    assert reporting.history == workflow.history


def test_case_queue_does_not_create_a_second_case():
    machine = create_machine()
    case = create_case(machine)

    queue = CaseQueue()
    queue.add_case(case)

    assert len(queue.cases) == 1
    assert queue.cases[0] is case


def test_dashboard_does_not_create_a_second_machine_or_case():
    machine = create_machine()
    case = create_case(machine)

    dashboard = TechnicianDashboard()
    dashboard.add_machine(machine)
    dashboard.add_case(case)

    assert len(dashboard.machines) == 1
    assert len(dashboard.cases) == 1
    assert dashboard.machines[0] is machine
    assert dashboard.cases[0] is case


def test_handoff_does_not_change_workflow_state():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    original_state = workflow.state

    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Additional investigation required.",
    )

    handoff.accept()

    assert handoff.status == "ACCEPTED"
    assert workflow.state == original_state


def test_notes_do_not_change_workflow_state():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    original_state = workflow.state

    notes = TechnicianNotes(case)
    notes.add_note("Technician note.")

    assert workflow.state == original_state
    assert notes.note_count == 1


def test_reporting_is_read_only_for_workflow_state():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    original_state = workflow.state
    reporting = CaseReporting(workflow)

    _ = reporting.summary

    assert workflow.state == original_state


def test_complete_local_operations_surface_preserves_single_case_identity():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    dashboard = TechnicianDashboard()
    overview = MachineOverview(machine)
    queue = CaseQueue()
    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    notes = TechnicianNotes(case)
    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Additional investigation required.",
    )
    reporting = CaseReporting(workflow)

    dashboard.add_machine(machine)
    dashboard.add_case(case)
    overview.add_case(case)
    queue.add_case(case)
    notes.add_note("Initial investigation note.")

    surfaces = [
        dashboard.cases[0],
        overview.cases[0],
        queue.cases[0],
        workspace.case,
        timeline.case,
        notes.case,
        handoff.case,
        reporting.case,
    ]

    assert all(surface is case for surface in surfaces)


def test_complete_local_case_flow_preserves_machine_identity():
    machine = create_machine()
    case = create_case(machine)
    workflow = create_workflow(case)

    overview = MachineOverview(machine)
    workspace = TechnicianWorkspace(workflow)
    timeline = CaseTimeline(workflow)
    handoff = CaseHandoff(
        workflow,
        recipient="technician-002",
        reason="Additional investigation required.",
    )
    reporting = CaseReporting(workflow)

    overview.add_case(case)

    assert overview.machine is machine
    assert case.machine_id == machine.machine_id
    assert workspace.machine_id == machine.machine_id
    assert timeline.machine_id == machine.machine_id
    assert handoff.machine_id == machine.machine_id
    assert reporting.machine_id == machine.machine_id