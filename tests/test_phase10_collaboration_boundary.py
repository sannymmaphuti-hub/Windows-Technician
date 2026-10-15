from copy import deepcopy

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_collaboration_boundary import (
    TechnicianCollaborationBoundary,
)
from engine.technician_workflow import TechnicianWorkflow


def create_case():
    case = DiagnosticCase()
    case.machine_id = "M001"
    case.hostname = "PC-001"
    return case


def create_workflow():
    case = create_case()
    return TechnicianWorkflow(case)


def test_boundary_requires_canonical_workflow():
    with pytest.raises(ValueError):
        TechnicianCollaborationBoundary(object())


def test_boundary_reuses_existing_workflow():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.workflow is workflow


def test_boundary_reuses_existing_case():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.case is workflow.case


def test_boundary_preserves_case_identity():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.case_id == workflow.case.case_id


def test_boundary_preserves_machine_identity():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.machine_id == workflow.case.machine_id
    assert boundary.hostname == workflow.case.hostname


def test_boundary_preserves_workflow_state():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.state is workflow.state
    assert boundary.is_terminal is workflow.is_terminal


def test_case_projection_is_defensive():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    first = boundary.case_projection()
    first["case_id"] = "MUTATED"
    first["machine_id"] = "MUTATED"
    first["hostname"] = "MUTATED"

    second = boundary.case_projection()

    assert second["case_id"] == workflow.case.case_id
    assert second["machine_id"] == workflow.case.machine_id
    assert second["hostname"] == workflow.case.hostname


def test_projection_is_defensive():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    first = boundary.projection()
    second = boundary.projection()

    assert first == second
    assert first is not second
    assert first["case"] is not second["case"]


def test_projection_has_observational_surface_only():
    workflow = create_workflow()

    boundary = TechnicianCollaborationBoundary(workflow)

    projection = boundary.projection()

    assert set(projection) == {"case"}
    assert set(projection["case"]) == {
        "case_id",
        "machine_id",
        "hostname",
        "state",
        "is_terminal",
    }

    serialized = repr(projection)

    assert "authorize_remediation" not in serialized
    assert "execute_remediation" not in serialized
    assert "verify_remediation" not in serialized


def test_boundary_does_not_replace_canonical_case():
    workflow = create_workflow()
    original_case = workflow.case

    boundary = TechnicianCollaborationBoundary(workflow)

    assert boundary.case is original_case
    assert workflow.case is original_case
