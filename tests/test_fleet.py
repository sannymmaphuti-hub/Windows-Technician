# ==========================================
# Windows Technician v0.9
# ARCHITECTURE BOUNDARY TESTS
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.technician_workflow import TechnicianWorkflow


def create_machine(machine_id="machine-001", hostname="PC-001"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="AMD64",
        operating_system="Windows 11",
    )


def test_fleet_members_are_managed_machines():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    assert all(
        isinstance(member, ManagedMachine)
        for member in fleet.machines
    )


def test_fleet_does_not_create_machine_copies():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    assert fleet.get_machine(machine.machine_id) is machine


def test_remote_session_remains_machine_scoped():
    machine = create_machine()
    session = RemoteSession(machine)

    assert session.machine is machine
    assert session.machine.machine_id == machine.machine_id


def test_diagnostic_case_remains_independent_from_fleet():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname

    assert case.machine_id == machine.machine_id
    assert not hasattr(fleet, "case")


def test_fleet_does_not_own_technician_workflow():
    fleet = Fleet("Test Fleet")

    assert not hasattr(fleet, "workflow")


def test_technician_workflow_remains_case_scoped():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert not hasattr(workflow, "fleet")


def test_fleet_does_not_become_a_diagnostic_case():
    fleet = Fleet("Test Fleet")

    assert not isinstance(fleet, DiagnosticCase)


def test_fleet_does_not_become_a_remote_session():
    fleet = Fleet("Test Fleet")

    assert not isinstance(fleet, RemoteSession)


def test_fleet_members_remain_isolated_objects():
    fleet = Fleet("Test Fleet")

    first = create_machine(
        machine_id="machine-001",
        hostname="PC-001",
    )

    second = create_machine(
        machine_id="machine-002",
        hostname="PC-002",
    )

    fleet.add_machine(first)
    fleet.add_machine(second)

    first.connection_state = "CONNECTED"

    assert first.connection_state == "CONNECTED"
    assert second.connection_state == "UNKNOWN"


def test_removing_machine_does_not_destroy_machine_object():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)
    removed = fleet.remove_machine(machine.machine_id)

    assert removed is machine
    assert removed.machine_id == "machine-001"
    assert removed.hostname == "PC-001"


def test_fleet_has_no_duplicate_case_hierarchy():
    fleet = Fleet("Test Fleet")

    forbidden_names = {
        "FleetCase",
        "FleetWorkflow",
        "FleetDiagnostic",
        "FleetRemediation",
    }

    assert not any(
        hasattr(fleet, name)
        for name in forbidden_names
    )


def test_fleet_has_no_independent_authorization_state():
    fleet = Fleet("Test Fleet")

    assert not hasattr(fleet, "authorization_status")
    assert not hasattr(fleet, "authorized")


def test_fleet_membership_does_not_authorize_remediation():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    assert not hasattr(machine, "authorized")
    assert not hasattr(fleet, "authorized")


def test_fleet_is_an_orchestration_scope_not_a_machine():
    fleet = Fleet("Test Fleet")

    assert not isinstance(fleet, ManagedMachine)


def test_same_machine_can_be_retrieved_by_canonical_machine_id():
    fleet = Fleet("Test Fleet")
    machine = create_machine(
        machine_id="canonical-machine-id",
        hostname="PC-001",
    )

    fleet.add_machine(machine)

    retrieved = fleet.get_machine(
        "canonical-machine-id"
    )

    assert retrieved is machine

# ============================================================
# V1.0 FLEET COMPOSITION CONTRACT
# ============================================================

def test_v1_0_fleet_machine_membership_is_identity_keyed():
    fleet = Fleet("V1.0 Fleet")
    first = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")
    second = ManagedMachine("MACHINE-002", "PC-002", "x86_64", "Windows 11")

    fleet.add_machine(first)
    fleet.add_machine(second)

    assert fleet.machine_ids == [
        first.machine_id,
        second.machine_id,
    ]
    assert fleet.machine_count == 2
    assert fleet.get_machine(first.machine_id) is first
    assert fleet.get_machine(second.machine_id) is second


def test_v1_0_fleet_machine_projection_is_defensive():
    fleet = Fleet("V1.0 Fleet")
    machine = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")

    fleet.add_machine(machine)

    members = fleet.machines
    members.clear()

    assert fleet.machine_count == 1
    assert fleet.get_machine(machine.machine_id) is machine


def test_v1_0_fleet_rejects_duplicate_machine_identity():
    fleet = Fleet("V1.0 Fleet")

    first = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")
    duplicate = ManagedMachine("MACHINE-001", "PC-OTHER", "x86_64", "Windows 11")

    fleet.add_machine(first)

    with pytest.raises(ValueError):
        fleet.add_machine(duplicate)

    assert fleet.machine_count == 1
    assert fleet.get_machine("MACHINE-001") is first


def test_v1_0_fleet_state_partitions_are_mutually_consistent():
    fleet = Fleet("V1.0 Fleet")

    connected = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")
    disconnected = ManagedMachine("MACHINE-002", "PC-002", "x86_64", "Windows 11")
    unknown = ManagedMachine("MACHINE-003", "PC-003", "x86_64", "Windows 11")

    connected.connection_state = "CONNECTED"
    disconnected.connection_state = "DISCONNECTED"
    unknown.connection_state = "UNKNOWN"

    connected.health_state = "HEALTHY"
    disconnected.health_state = "WARNING"
    unknown.health_state = "UNKNOWN"

    fleet.add_machine(connected)
    fleet.add_machine(disconnected)
    fleet.add_machine(unknown)

    assert len(fleet.connected_machines) == 1
    assert len(fleet.disconnected_machines) == 1
    assert len(fleet.unknown_connection_machines) == 1

    assert len(fleet.healthy_machines) == 1
    assert len(fleet.warning_machines) == 1
    assert len(fleet.unknown_health_machines) == 1

    assert (
        len(fleet.connected_machines)
        + len(fleet.disconnected_machines)
        + len(fleet.unknown_connection_machines)
        == fleet.machine_count
    )

    assert (
        len(fleet.healthy_machines)
        + len(fleet.warning_machines)
        + len(fleet.unknown_health_machines)
        == fleet.machine_count
    )


def test_v1_0_fleet_summary_matches_membership_state():
    fleet = Fleet("V1.0 Fleet")

    first = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")
    second = ManagedMachine("MACHINE-002", "PC-002", "x86_64", "Windows 11")

    first.connection_state = "CONNECTED"
    second.connection_state = "DISCONNECTED"

    first.health_state = "HEALTHY"
    second.health_state = "WARNING"

    fleet.add_machine(first)
    fleet.add_machine(second)

    summary = fleet.summary

    assert summary["fleet_id"] == fleet.fleet_id
    assert summary["name"] == "V1.0 Fleet"
    assert summary["machine_count"] == 2
    assert summary["connected_count"] == 1
    assert summary["disconnected_count"] == 1
    assert summary["healthy_count"] == 1
    assert summary["warning_count"] == 1


def test_v1_0_fleet_intelligence_is_non_authoritative_aggregation():
    fleet = Fleet("V1.0 Fleet")

    first = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")
    second = ManagedMachine("MACHINE-002", "PC-002", "x86_64", "Windows 11")

    first.health_state = "HEALTHY"
    second.health_state = "WARNING"

    first.connection_state = "CONNECTED"
    second.connection_state = "CONNECTED"

    fleet.add_machine(first)
    fleet.add_machine(second)

    intelligence = fleet.intelligence

    assert intelligence["machine_count"] == 2
    assert intelligence["healthy_count"] == 1
    assert intelligence["warning_count"] == 1
    assert intelligence["dominant_health_state"] is None
    assert intelligence["connected_count"] == 2
    assert intelligence["dominant_connection_state"] == "CONNECTED"


def test_v1_0_fleet_remove_preserves_machine_object():
    fleet = Fleet("V1.0 Fleet")
    machine = ManagedMachine("MACHINE-001", "PC-001", "x86_64", "Windows 11")

    fleet.add_machine(machine)

    removed = fleet.remove_machine(machine.machine_id)

    assert removed is machine
    assert fleet.machine_count == 0
    assert fleet.get_machine(machine.machine_id) is None

    machine.health_state = "WARNING"

    assert machine.health_state == "WARNING"


def test_v1_0_fleet_unknown_lookup_is_safe():
    fleet = Fleet("V1.0 Fleet")

    assert fleet.get_machine("MISSING") is None
    assert fleet.contains_machine("MISSING") is False
    assert fleet.remove_machine("MISSING") is None
    assert fleet.find_by_hostname("MISSING") is None
