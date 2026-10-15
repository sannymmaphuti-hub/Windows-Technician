from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.fleet_alert_aggregation import FleetAlertAggregation


def make_machine(machine_id, hostname):
    return ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )


def make_alert(machine, alert_type):
    return ProactiveAlert(
        machine=machine,
        alert_type=alert_type,
        metric="memory",
        message="Memory usage requires attention.",
    )


def test_alert_aggregation_projects_only_fleet_alerts():
    fleet = Fleet("Production Fleet")

    machine = make_machine("MACHINE-001", "PC-001")
    external_machine = make_machine("MACHINE-999", "EXTERNAL-999")

    fleet.add_machine(machine)

    fleet_alert = make_alert(machine, "MEMORY_WARNING")
    external_alert = make_alert(external_machine, "CPU_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [fleet_alert, external_alert],
    )

    assert aggregation.alerts == [fleet_alert]
    assert aggregation.alert_count == 1


def test_active_and_acknowledged_alerts_are_separated():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    active = make_alert(machine, "MEMORY_WARNING")
    acknowledged = make_alert(machine, "CPU_WARNING")
    acknowledged.acknowledge()

    aggregation = FleetAlertAggregation(
        fleet,
        [active, acknowledged],
    )

    assert aggregation.active_alert_count == 1
    assert aggregation.acknowledged_alert_count == 1
    assert aggregation.active_alerts()[0]["alert_type"] == "MEMORY_WARNING"
    assert aggregation.acknowledged_alerts()[0]["alert_type"] == "CPU_WARNING"


def test_visible_alerts_include_active_and_acknowledged():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    active = make_alert(machine, "MEMORY_WARNING")
    acknowledged = make_alert(machine, "CPU_WARNING")
    acknowledged.acknowledge()

    aggregation = FleetAlertAggregation(
        fleet,
        [active, acknowledged],
    )

    visible = aggregation.visible_alerts()

    assert len(visible) == 2
    assert {alert["alert_type"] for alert in visible} == {
        "MEMORY_WARNING",
        "CPU_WARNING",
    }


def test_alerts_by_machine_groups_alerts():
    fleet = Fleet("Production Fleet")

    first_machine = make_machine("MACHINE-001", "PC-001")
    second_machine = make_machine("MACHINE-002", "PC-002")

    fleet.add_machine(first_machine)
    fleet.add_machine(second_machine)

    first = make_alert(first_machine, "MEMORY_WARNING")
    second = make_alert(second_machine, "CPU_WARNING")
    third = make_alert(first_machine, "DISK_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [first, second, third],
    )

    grouped = aggregation.alerts_by_machine()

    assert set(grouped) == {
        "MACHINE-001",
        "MACHINE-002",
    }

    assert [alert["alert_type"] for alert in grouped["MACHINE-001"]] == [
        "MEMORY_WARNING",
        "DISK_WARNING",
    ]

    assert [alert["alert_type"] for alert in grouped["MACHINE-002"]] == [
        "CPU_WARNING",
    ]


def test_alert_type_counts_reflect_fleet_alerts():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    first = make_alert(machine, "MEMORY_WARNING")
    second = make_alert(machine, "MEMORY_WARNING")
    third = make_alert(machine, "CPU_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [first, second, third],
    )

    assert aggregation.alert_type_counts() == {
        "MEMORY_WARNING": 2,
        "CPU_WARNING": 1,
    }


def test_affected_machine_ids_are_unique_and_ordered():
    fleet = Fleet("Production Fleet")

    first_machine = make_machine("MACHINE-001", "PC-001")
    second_machine = make_machine("MACHINE-002", "PC-002")

    fleet.add_machine(first_machine)
    fleet.add_machine(second_machine)

    first = make_alert(first_machine, "MEMORY_WARNING")
    second = make_alert(second_machine, "CPU_WARNING")
    third = make_alert(first_machine, "DISK_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [first, second, third],
    )

    assert aggregation.affected_machine_ids() == [
        "MACHINE-001",
        "MACHINE-002",
    ]


def test_alert_projection_is_defensive():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    alert = make_alert(machine, "MEMORY_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [alert],
    )

    projected = aggregation.active_alerts()

    projected[0]["message"] = "tampered"

    assert aggregation.active_alerts()[0]["message"] == (
        "Memory usage requires attention."
    )


def test_projection_contains_complete_alert_surface():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    alert = make_alert(machine, "MEMORY_WARNING")

    aggregation = FleetAlertAggregation(
        fleet,
        [alert],
    )

    projection = aggregation.projection()

    assert set(projection) == {
        "alert_count",
        "active_alert_count",
        "acknowledged_alert_count",
        "affected_machine_ids",
        "alert_type_counts",
        "active_alerts",
        "acknowledged_alerts",
        "visible_alerts",
        "alerts_by_machine",
    }

    projected_alert = projection["active_alerts"][0]

    assert projected_alert == {
        "machine_id": "MACHINE-001",
        "hostname": "PC-001",
        "alert_type": "MEMORY_WARNING",
        "metric": "memory",
        "message": "Memory usage requires attention.",
        "status": "ACTIVE",
    }
