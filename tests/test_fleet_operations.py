# ==========================================
# Windows Technician v0.9
# FLEET OPERATIONS TESTS
# ==========================================

import pytest

from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine


def create_machine(
    machine_id="machine-001",
    hostname="PC-001",
):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="AMD64",
        operating_system="Windows 11",
    )


def test_fleet_can_report_machine_ids():
    fleet = Fleet("Test Fleet")

    first = create_machine("machine-001", "PC-001")
    second = create_machine("machine-002", "PC-002")

    fleet.add_machine(first)
    fleet.add_machine(second)

    assert fleet.machine_ids == [
        "machine-001",
        "machine-002",
    ]


def test_fleet_can_report_connected_machines():
    fleet = Fleet("Test Fleet")

    connected = create_machine("machine-001", "PC-001")
    disconnected = create_machine("machine-002", "PC-002")

    connected.connection_state = "CONNECTED"
    disconnected.connection_state = "DISCONNECTED"

    fleet.add_machine(connected)
    fleet.add_machine(disconnected)

    assert fleet.connected_machines == [connected]


def test_fleet_can_report_disconnected_machines():
    fleet = Fleet("Test Fleet")

    connected = create_machine("machine-001", "PC-001")
    disconnected = create_machine("machine-002", "PC-002")

    connected.connection_state = "CONNECTED"
    disconnected.connection_state = "DISCONNECTED"

    fleet.add_machine(connected)
    fleet.add_machine(disconnected)

    assert fleet.disconnected_machines == [disconnected]


def test_fleet_can_report_unknown_connection_machines():
    fleet = Fleet("Test Fleet")

    known = create_machine("machine-001", "PC-001")
    unknown = create_machine("machine-002", "PC-002")

    known.connection_state = "CONNECTED"

    fleet.add_machine(known)
    fleet.add_machine(unknown)

    assert fleet.unknown_connection_machines == [unknown]


def test_fleet_can_report_machine_health_states():
    fleet = Fleet("Test Fleet")

    healthy = create_machine("machine-001", "PC-001")
    warning = create_machine("machine-002", "PC-002")
    unknown = create_machine("machine-003", "PC-003")

    healthy.health_state = "HEALTHY"
    warning.health_state = "WARNING"

    fleet.add_machine(healthy)
    fleet.add_machine(warning)
    fleet.add_machine(unknown)

    assert fleet.healthy_machines == [healthy]
    assert fleet.warning_machines == [warning]
    assert fleet.unknown_health_machines == [unknown]


def test_fleet_can_find_machine_by_hostname():
    fleet = Fleet("Test Fleet")

    first = create_machine("machine-001", "PC-001")
    second = create_machine("machine-002", "PC-002")

    fleet.add_machine(first)
    fleet.add_machine(second)

    assert fleet.find_by_hostname("PC-001") is first
    assert fleet.find_by_hostname("PC-002") is second


def test_find_by_hostname_returns_none_when_not_found():
    fleet = Fleet("Test Fleet")

    fleet.add_machine(create_machine())

    assert fleet.find_by_hostname("UNKNOWN-PC") is None


def test_fleet_summary_reports_current_machine_state():
    fleet = Fleet("Test Fleet")

    connected_healthy = create_machine(
        "machine-001",
        "PC-001",
    )
    connected_warning = create_machine(
        "machine-002",
        "PC-002",
    )
    disconnected = create_machine(
        "machine-003",
        "PC-003",
    )

    connected_healthy.connection_state = "CONNECTED"
    connected_healthy.health_state = "HEALTHY"

    connected_warning.connection_state = "CONNECTED"
    connected_warning.health_state = "WARNING"

    disconnected.connection_state = "DISCONNECTED"

    fleet.add_machine(connected_healthy)
    fleet.add_machine(connected_warning)
    fleet.add_machine(disconnected)

    summary = fleet.summary

    assert summary["fleet_id"] == fleet.fleet_id
    assert summary["name"] == "Test Fleet"
    assert summary["machine_count"] == 3
    assert summary["connected_count"] == 2
    assert summary["disconnected_count"] == 1
    assert summary["unknown_connection_count"] == 0
    assert summary["healthy_count"] == 1
    assert summary["warning_count"] == 1
    assert summary["unknown_health_count"] == 1


def test_fleet_operations_are_read_only():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    machine.connection_state = "CONNECTED"
    fleet.add_machine(machine)

    machines = fleet.connected_machines
    machines.clear()

    assert fleet.machine_count == 1
    assert fleet.connected_machines == [machine]


def test_fleet_operations_do_not_change_machine_state():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    machine.connection_state = "CONNECTED"
    machine.health_state = "HEALTHY"

    fleet.add_machine(machine)

    _ = fleet.summary
    _ = fleet.connected_machines
    _ = fleet.healthy_machines

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "HEALTHY"


def test_fleet_operations_do_not_create_diagnostic_cases():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    _ = fleet.summary

    assert not hasattr(fleet, "cases")
    assert not hasattr(fleet, "diagnostic_cases")


def test_fleet_operations_do_not_create_authorization():
    fleet = Fleet("Test Fleet")
    machine = create_machine()

    fleet.add_machine(machine)

    _ = fleet.summary

    assert not hasattr(fleet, "authorization_status")
    assert not hasattr(fleet, "authorized")


def test_empty_fleet_summary_is_safe():
    fleet = Fleet("Empty Fleet")

    summary = fleet.summary

    assert summary["machine_count"] == 0
    assert summary["connected_count"] == 0
    assert summary["disconnected_count"] == 0
    assert summary["unknown_connection_count"] == 0
    assert summary["healthy_count"] == 0
    assert summary["warning_count"] == 0
    assert summary["unknown_health_count"] == 0