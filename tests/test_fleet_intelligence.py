# ==========================================
# Windows Technician v0.9
# FLEET INTELLIGENCE TESTS
# ==========================================

from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine


def create_machine(
    machine_id,
    hostname,
    connection_state="UNKNOWN",
    health_state="UNKNOWN",
):
    machine = ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="AMD64",
        operating_system="Windows 11",
    )

    machine.connection_state = connection_state
    machine.health_state = health_state

    return machine


def test_fleet_can_count_health_states():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
            health_state="HEALTHY",
        )
    )
    fleet.add_machine(
        create_machine(
            "machine-002",
            "PC-002",
            health_state="WARNING",
        )
    )
    fleet.add_machine(
        create_machine(
            "machine-003",
            "PC-003",
            health_state="WARNING",
        )
    )

    intelligence = fleet.intelligence

    assert intelligence["machine_count"] == 3
    assert intelligence["healthy_count"] == 1
    assert intelligence["warning_count"] == 2


def test_fleet_can_identify_health_concentration():
    fleet = Fleet("Production Fleet")

    for index in range(4):
        fleet.add_machine(
            create_machine(
                f"machine-{index}",
                f"PC-{index}",
                health_state="WARNING",
            )
        )

    fleet.add_machine(
        create_machine(
            "machine-healthy",
            "PC-HEALTHY",
            health_state="HEALTHY",
        )
    )

    intelligence = fleet.intelligence

    assert intelligence["dominant_health_state"] == "WARNING"


def test_fleet_reports_no_dominant_health_state_when_tied():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
            health_state="HEALTHY",
        )
    )
    fleet.add_machine(
        create_machine(
            "machine-002",
            "PC-002",
            health_state="WARNING",
        )
    )

    intelligence = fleet.intelligence

    assert intelligence["dominant_health_state"] is None


def test_fleet_can_identify_connection_concentration():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
            connection_state="CONNECTED",
        )
    )
    fleet.add_machine(
        create_machine(
            "machine-002",
            "PC-002",
            connection_state="CONNECTED",
        )
    )
    fleet.add_machine(
        create_machine(
            "machine-003",
            "PC-003",
            connection_state="DISCONNECTED",
        )
    )

    intelligence = fleet.intelligence

    assert intelligence["dominant_connection_state"] == "CONNECTED"


def test_empty_fleet_has_no_dominant_state():
    fleet = Fleet("Empty Fleet")

    intelligence = fleet.intelligence

    assert intelligence["machine_count"] == 0
    assert intelligence["dominant_health_state"] is None
    assert intelligence["dominant_connection_state"] is None


def test_fleet_intelligence_does_not_modify_machines():
    fleet = Fleet("Production Fleet")

    machine = create_machine(
        "machine-001",
        "PC-001",
        connection_state="CONNECTED",
        health_state="WARNING",
    )

    fleet.add_machine(machine)

    _ = fleet.intelligence

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "WARNING"


def test_fleet_intelligence_does_not_authorize_remediation():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
            health_state="WARNING",
        )
    )

    intelligence = fleet.intelligence

    assert "authorized" not in intelligence
    assert "authorization_status" not in intelligence
    assert "remediation" not in intelligence


def test_fleet_intelligence_does_not_create_cases():
    fleet = Fleet("Production Fleet")

    fleet.add_machine(
        create_machine(
            "machine-001",
            "PC-001",
            health_state="WARNING",
        )
    )

    _ = fleet.intelligence

    assert not hasattr(fleet, "diagnostic_cases")
    assert not hasattr(fleet, "cases")