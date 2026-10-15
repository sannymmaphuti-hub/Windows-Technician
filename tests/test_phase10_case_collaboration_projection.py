from engine.case_collaboration_projection import (
    CaseCollaborationProjection,
)
from engine.case_ownership import CaseOwnership
from engine.case_status_coordination import CaseStatusCoordinator
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.technician_collaboration_boundary import (
    TechnicianCollaborationBoundary,
)
from engine.technician_identity import TechnicianIdentity
from engine.technician_workflow import TechnicianWorkflow


def create_components():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"

    workflow = TechnicianWorkflow(case)

    boundary = TechnicianCollaborationBoundary(workflow)

    technician = TechnicianIdentity(
        technician_id="TECH-001",
        name="Alice",
    )

    ownership = CaseOwnership(case, technician)
    status = CaseStatusCoordinator(workflow)
    timeline = CaseTimeline(case)

    return case, boundary, ownership, status, timeline


def create_projection():
    return CaseCollaborationProjection(
        *create_components()[1:]
    )


def test_projection_creation():
    projection = create_projection()

    assert projection.case_id


def test_projection_contains_case():
    projection = create_projection().projection()

    assert "case" in projection
    assert projection["case"]["case_id"] == projection["ownership"]["case_id"]


def test_projection_contains_ownership():
    projection = create_projection().projection()

    assert projection["ownership"]["is_owned"] is True
    assert projection["ownership"]["owner_id"] == "TECH-001"


def test_projection_contains_status():
    projection = create_projection().projection()

    assert projection["status"]["state"] == "OPEN"
    assert projection["status"]["status"] == "OPEN"
    assert projection["status"]["is_active"] is True
    assert projection["status"]["is_terminal"] is False


def test_projection_contains_timeline():
    projection = create_projection().projection()

    assert projection["timeline"]["entry_count"] == 0
    assert projection["timeline"]["entries"] == []


def test_projection_contains_current_technician():
    projection = create_projection().projection()

    assert projection["technician"]["technician_id"] == "TECH-001"
    assert projection["technician"]["name"] == "Alice"


def test_unowned_case_has_no_current_technician():
    case, boundary, ownership, status, timeline = create_components()

    ownership.clear()

    projection = CaseCollaborationProjection(
        boundary,
        ownership,
        status,
        timeline,
    ).projection()

    assert projection["technician"] is None


def test_projection_is_defensive():
    projection = create_projection()

    data = projection.projection()

    data["ownership"]["owner"]["name"] = "Changed"
    data["status"]["status"] = "Changed"
    data["case"]["hostname"] = "Changed"

    fresh = projection.projection()

    assert fresh["ownership"]["owner"]["name"] == "Alice"
    assert fresh["status"]["status"] == "OPEN"
    assert fresh["case"]["hostname"] == "TEST-PC"


def test_components_must_reference_same_case():
    case, boundary, ownership, status, timeline = create_components()

    other_case = DiagnosticCase()
    other_ownership = CaseOwnership(
        other_case,
        TechnicianIdentity(
            technician_id="TECH-002",
            name="Bob",
        ),
    )

    try:
        CaseCollaborationProjection(
            boundary,
            other_ownership,
            status,
            timeline,
        )
        assert False
    except ValueError:
        pass


def test_projection_does_not_change_workflow():
    case, boundary, ownership, status, timeline = create_components()

    workflow = boundary.workflow
    initial_state = workflow.state

    CaseCollaborationProjection(
        boundary,
        ownership,
        status,
        timeline,
    ).projection()

    assert workflow.state == initial_state
