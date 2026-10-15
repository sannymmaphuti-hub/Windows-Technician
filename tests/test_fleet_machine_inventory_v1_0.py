import pytest

from engine.fleet import Fleet
from engine.fleet_machine_inventory import FleetMachineInventory
from engine.managed_machine import ManagedMachine


def make_machine(
    machine_id,
    hostname,
    connection_state="CONNECTED",
    health_state="HEALTHY",
):
    machine = ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )
    machine.connection_state = connection_state
    machine.health_state = health_state
    return machine


def test_inventory_requires_fleet():
    with pytest.raises(ValueError):
        FleetMachineInventory(None)


def test_inventory_reports_fleet_machine_count():
    fleet = Fleet("Production Fleet")
    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )
    fleet.add_machine(
        make_machine("MACHINE-002", "PC-002")
    )

    inventory = FleetMachineInventory(fleet)

    assert inventory.machine_count == 2


def test_inventory_projects_complete_machine_identity_and_state():
    fleet = Fleet("Production Fleet")

    machine = make_machine(
        "MACHINE-001",
        "PC-001",
        connection_state="CONNECTED",
        health_state="WARNING",
    )

    fleet.add_machine(machine)

    inventory = FleetMachineInventory(fleet)

    projection = inventory.get_machine("MACHINE-001")

    assert projection == {
        "machine_id": "MACHINE-001",
        "hostname": "PC-001",
        "platform": "x86_64",
        "operating_system": "Windows 11",
        "connection_state": "CONNECTED",
        "health_state": "WARNING",
        "last_seen": machine.last_seen,
    }


def test_inventory_returns_all_fleet_members_in_membership_order():
    fleet = Fleet("Production Fleet")

    first = make_machine("MACHINE-001", "PC-001")
    second = make_machine("MACHINE-002", "PC-002")

    fleet.add_machine(first)
    fleet.add_machine(second)

    inventory = FleetMachineInventory(fleet)

    assert [
        machine["machine_id"]
        for machine in inventory.machines()
    ] == [
        "MACHINE-001",
        "MACHINE-002",
    ]


def test_inventory_machine_snapshots_are_defensive():
    fleet = Fleet("Production Fleet")
    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    inventory = FleetMachineInventory(fleet)

    machines = inventory.machines()
    machines[0]["hostname"] = "CHANGED"

    assert inventory.get_machine("MACHINE-001")["hostname"] == "PC-001"


def test_inventory_missing_machine_returns_none():
    fleet = Fleet("Production Fleet")
    inventory = FleetMachineInventory(fleet)

    assert inventory.get_machine("MISSING") is None


def test_inventory_connection_filters_use_canonical_fleet_state():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine(
            "MACHINE-001",
            "PC-001",
            connection_state="CONNECTED",
        )
    )
    fleet.add_machine(
        make_machine(
            "MACHINE-002",
            "PC-002",
            connection_state="DISCONNECTED",
        )
    )

    inventory = FleetMachineInventory(fleet)

    assert [
        machine["machine_id"]
        for machine in inventory.connected_machines()
    ] == ["MACHINE-001"]

    assert [
        machine["machine_id"]
        for machine in inventory.disconnected_machines()
    ] == ["MACHINE-002"]


def test_inventory_health_filters_use_canonical_fleet_state():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        make_machine(
            "MACHINE-001",
            "PC-001",
            health_state="HEALTHY",
        )
    )
    fleet.add_machine(
        make_machine(
            "MACHINE-002",
            "PC-002",
            health_state="WARNING",
        )
    )

    inventory = FleetMachineInventory(fleet)

    assert [
        machine["machine_id"]
        for machine in inventory.healthy_machines()
    ] == ["MACHINE-001"]

    assert [
        machine["machine_id"]
        for machine in inventory.warning_machines()
    ] == ["MACHINE-002"]


def test_inventory_projection_contains_fleet_and_machine_surfaces():
    fleet = Fleet("Production Fleet")
    fleet.add_machine(
        make_machine("MACHINE-001", "PC-001")
    )

    inventory = FleetMachineInventory(fleet)

    projection = inventory.inventory_projection()

    assert set(projection) == {
        "fleet",
        "machines",
    }

    assert projection["fleet"]["fleet_id"] == fleet.fleet_id
    assert projection["fleet"]["name"] == "Production Fleet"
    assert projection["fleet"]["machine_count"] == 1
    assert len(projection["machines"]) == 1
