from engine.case_collaboration_projection import (
    CaseCollaborationProjection,
)
from engine.case_handoff import CaseHandoff
from engine.case_note import CaseNote
from engine.case_ownership import CaseOwnership
from engine.case_status_coordination import CaseStatusCoordinator
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.technician_collaboration_boundary import (
    TechnicianCollaborationBoundary,
)
from engine.technician_identity import TechnicianIdentity
from engine.technician_workflow import TechnicianWorkflow


def create_context():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"

    workflow = TechnicianWorkflow(case)

    technician = TechnicianIdentity(
        technician_id="TECH-001",
        name="Alice",
    )

    ownership = CaseOwnership(case, technician)
    boundary = TechnicianCollaborationBoundary(workflow)
    status = CaseStatusCoordinator(workflow)
    timeline = CaseTimeline(case)

    projection = CaseCollaborationProjection(
        boundary,
        ownership,
        status,
        timeline,
    )

    return (
        case,
        workflow,
        technician,
        ownership,
        boundary,
        status,
        timeline,
        projection,
    )


def test_note_does_not_change_workflow():
    case, workflow, technician, *_ = create_context()

    initial_state = workflow.state

    CaseNote(
        case,
        technician,
        "Investigating the reported issue.",
    )

    assert workflow.state == initial_state


def test_timeline_does_not_change_workflow():
    case, workflow, technician, ownership, _, _, timeline, _ = (
        create_context()
    )

    initial_state = workflow.state

    note = CaseNote(
        case,
        technician,
        "Investigation recorded.",
    )

    timeline.add_note(note)

    assert workflow.state == initial_state


def test_handoff_does_not_change_workflow():
    case, workflow, technician, ownership, *_ = create_context()

    recipient = TechnicianIdentity(
        technician_id="TECH-002",
        name="Bob",
    )

    initial_state = workflow.state

    handoff = CaseHandoff(
        ownership,
        recipient,
        technician,
        reason="Specialist required.",
    )

    handoff.apply()

    assert workflow.state == initial_state


def test_handoff_only_changes_ownership():
    case, workflow, technician, ownership, *_ = create_context()

    recipient = TechnicianIdentity(
        technician_id="TECH-002",
        name="Bob",
    )

    initial_state = workflow.state

    CaseHandoff(
        ownership,
        recipient,
        technician,
    ).apply()

    assert ownership.owner_id == "TECH-002"
    assert workflow.state == initial_state


def test_projection_is_read_only_for_workflow():
    case, workflow, *_rest = create_context()

    initial_state = workflow.state

    projection = _rest[-1].projection()

    assert projection["status"]["state"] == initial_state.value
    assert workflow.state == initial_state


def test_collaboration_boundary_exposes_no_remediation_execution():
    _, _, _, _, boundary, *_ = create_context()

    assert not hasattr(boundary, "execute")
    assert not hasattr(boundary, "remediate")
    assert not hasattr(boundary, "authorize")
    assert not hasattr(boundary, "diagnose")


def test_status_coordinator_exposes_no_remediation_execution():
    _, _, _, _, _, status, *_ = create_context()

    assert not hasattr(status, "execute")
    assert not hasattr(status, "remediate")
    assert not hasattr(status, "authorize")


def test_timeline_exposes_no_technical_execution():
    _, _, _, _, _, _, timeline, _ = create_context()

    assert not hasattr(timeline, "execute")
    assert not hasattr(timeline, "remediate")
    assert not hasattr(timeline, "diagnose")


def test_projection_contains_only_collaboration_surfaces():
    _, _, _, _, _, _, _, projection = create_context()

    data = projection.projection()

    assert set(data) == {
        "case",
        "ownership",
        "status",
        "timeline",
        "technician",
    }


def test_collaboration_projection_does_not_mutate_case():
    case, workflow, technician, ownership, boundary, status, timeline, projection = (
        create_context()
    )

    initial_state = workflow.state
    initial_case_id = case.case_id

    projection.projection()

    assert case.case_id == initial_case_id
    assert workflow.state == initial_state
    assert ownership.case_id == initial_case_id
    assert timeline.case_id == initial_case_id
