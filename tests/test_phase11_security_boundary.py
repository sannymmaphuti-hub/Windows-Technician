from engine.case_collaboration_projection import CaseCollaborationProjection
from engine.case_ownership import CaseOwnership
from engine.case_status_coordination import CaseStatusCoordinator
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.technician_collaboration_boundary import TechnicianCollaborationBoundary
from engine.technician_identity import TechnicianIdentity
from engine.technician_workflow import TechnicianWorkflow


def create_context():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"

    workflow = TechnicianWorkflow(case)
    boundary = TechnicianCollaborationBoundary(workflow)

    technician = TechnicianIdentity(
        technician_id="TECH-001",
        name="Alice",
        role="TECHNICIAN",
    )

    ownership = CaseOwnership(case, technician)
    status = CaseStatusCoordinator(workflow)
    timeline = CaseTimeline(case)

    projection = CaseCollaborationProjection(
        boundary,
        ownership,
        status,
        timeline,
    )

    return case, workflow, technician, ownership, projection


def test_security_boundary_requires_existing_technician_identity():
    _, _, technician, _, _ = create_context()

    assert technician.technician_id == "TECH-001"
    assert technician.role == "TECHNICIAN"


def test_security_boundary_uses_canonical_case():
    case, _, _, ownership, projection = create_context()

    assert ownership.case is case
    assert projection.case_id == case.case_id


def test_security_boundary_preserves_canonical_workflow():
    _, workflow, _, _, projection = create_context()

    initial_state = workflow.state

    projection.projection()

    assert workflow.state == initial_state


def test_security_boundary_does_not_execute_operations():
    _, _, _, _, projection = create_context()

    assert not hasattr(projection, "execute")
    assert not hasattr(projection, "remediate")
    assert not hasattr(projection, "authorize")


def test_security_boundary_does_not_grant_permissions_implicitly():
    _, _, technician, _, _ = create_context()

    assert not hasattr(technician, "permissions")
    assert not hasattr(technician, "can_execute")


def test_security_boundary_projection_is_defensive():
    _, _, _, _, projection = create_context()

    first = projection.projection()
    first["case"]["case_id"] = "TAMPERED"

    second = projection.projection()

    assert second["case"]["case_id"] != "TAMPERED"
