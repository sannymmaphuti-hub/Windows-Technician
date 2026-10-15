import pytest

from engine.case_status_coordination import CaseStatusCoordinator
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def create_case():
    case = DiagnosticCase()
    case.machine_id = "M001"
    case.hostname = "PC-001"
    return case


def create_workflow():
    return TechnicianWorkflow(create_case())


def progress_to_diagnosed(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()


def progress_to_action_required(workflow):
    progress_to_diagnosed(workflow)
    workflow.require_action()


def progress_to_remediating(workflow):
    progress_to_action_required(workflow)
    workflow.start_remediation()


def progress_to_verifying(workflow):
    progress_to_remediating(workflow)
    workflow.start_verification()


def test_coordinator_requires_workflow():
    with pytest.raises(ValueError):
        CaseStatusCoordinator(object())


def test_coordinator_reuses_canonical_workflow():
    workflow = create_workflow()

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.workflow is workflow
    assert coordinator.case is workflow.case


def test_open_state_is_active():
    workflow = create_workflow()
    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.state is workflow.state
    assert coordinator.status == "OPEN"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_investigating_state_is_active():
    workflow = create_workflow()
    workflow.start_investigation()

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "INVESTIGATING"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_diagnosed_state_is_active():
    workflow = create_workflow()
    progress_to_diagnosed(workflow)

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "DIAGNOSED"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_action_required_state_is_active():
    workflow = create_workflow()
    progress_to_action_required(workflow)

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "ACTION_REQUIRED"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_remediating_state_is_active():
    workflow = create_workflow()
    progress_to_remediating(workflow)

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "REMEDIATING"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_verifying_state_is_active():
    workflow = create_workflow()
    progress_to_verifying(workflow)

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "VERIFYING"
    assert coordinator.is_active is True
    assert coordinator.is_terminal is False


def test_resolved_state_is_terminal():
    workflow = create_workflow()
    progress_to_verifying(workflow)
    workflow.resolve()

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "RESOLVED"
    assert coordinator.is_active is False
    assert coordinator.is_terminal is True


def test_resolved_state_is_terminal():
    workflow = create_workflow()
    progress_to_verifying(workflow)
    workflow.resolve()

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "RESOLVED"
    assert coordinator.is_active is False
    assert coordinator.is_terminal is True


def test_status_tracks_workflow_without_cached_state():
    workflow = create_workflow()
    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.status == "OPEN"

    workflow.start_investigation()

    assert coordinator.status == "INVESTIGATING"
    assert coordinator.state is workflow.state


def test_projection_has_canonical_surface():
    workflow = create_workflow()
    coordinator = CaseStatusCoordinator(workflow)

    projection = coordinator.projection()

    assert set(projection) == {
        "case_id",
        "state",
        "status",
        "is_active",
        "is_terminal",
    }


def test_projection_is_defensive():
    workflow = create_workflow()
    coordinator = CaseStatusCoordinator(workflow)

    projection = coordinator.projection()
    projection["status"] = "MUTATED"

    assert coordinator.status == "OPEN"
    assert coordinator.projection()["status"] == "OPEN"


def test_coordinator_does_not_mutate_case():
    workflow = create_workflow()
    case = workflow.case
    original_case_id = case.case_id
    original_machine_id = case.machine_id

    coordinator = CaseStatusCoordinator(workflow)

    assert coordinator.case is case
    assert case.case_id == original_case_id
    assert case.machine_id == original_machine_id


def test_coordinator_has_no_remediation_controls():
    coordinator = CaseStatusCoordinator(create_workflow())

    assert not hasattr(coordinator, "authorize_remediation")
    assert not hasattr(coordinator, "execute_remediation")
    assert not hasattr(coordinator, "verify_remediation")


def test_repr_is_safe():
    coordinator = CaseStatusCoordinator(create_workflow())

    representation = repr(coordinator)

    assert coordinator.case_id in representation
    assert "authorize_remediation" not in representation
    assert "execute_remediation" not in representation
    assert "verify_remediation" not in representation
