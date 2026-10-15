from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_operational_projection import FleetOperationalProjection
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


def make_machine(machine_id, hostname, health_state=None):
    machine = ManagedMachine(
        machine_id,
        hostname,
        "x86_64",
        "Windows 11",
    )

    if health_state is not None:
        machine.health_state = health_state

    return machine


def make_alert(machine, alert_type):
    return ProactiveAlert(
        machine=machine,
        alert_type=alert_type,
        metric="memory",
        message="Memory usage requires attention.",
    )


def make_case(machine):
    case = DiagnosticCase()

    # DiagnosticCase is intentionally parameterless.
    # Fleet aggregation identifies a case by its machine identity.
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname

    return case


def test_projection_requires_canonical_fleet():
    try:
        FleetOperationalProjection(None)
    except ValueError as exc:
        assert "Fleet" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_projection_composes_inventory_health_cases_and_alerts():
    fleet = Fleet("Production Fleet")

    machine = make_machine(
        "MACHINE-001",
        "PC-001",
        health_state="HEALTHY",
    )
    fleet.add_machine(machine)

    case = make_case(machine)
    alert = make_alert(machine, "MEMORY_WARNING")

    projection = FleetOperationalProjection(
        fleet,
        cases=[case],
        alerts=[alert],
    )

    result = projection.projection()

    assert set(result) == {
        "fleet",
        "inventory",
        "health",
        "cases",
        "alerts",
    }

    assert result["fleet"]["name"] == "Production Fleet"
    assert result["inventory"]["machines"][0]["machine_id"] == "MACHINE-001"
    assert result["health"]["machine_count"] == 1
    assert result["health"]["overall_state"] == "HEALTHY"
    assert result["cases"]["case_count"] == 1
    assert result["alerts"]["alert_count"] == 1


def test_machine_inventory_is_available_as_independent_surface():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    projection = FleetOperationalProjection(fleet)

    result = projection.machine_inventory()

    assert result["fleet"]["machine_count"] == 1
    assert result["machines"][0]["hostname"] == "PC-001"


def test_health_projection_is_available_as_independent_surface():
    fleet = Fleet("Production Fleet")
    machine = make_machine(
        "MACHINE-001",
        "PC-001",
        health_state="HEALTHY",
    )
    fleet.add_machine(machine)

    projection = FleetOperationalProjection(fleet)

    result = projection.health_projection()

    assert result["machine_count"] == 1
    assert result["overall_state"] == "HEALTHY"
    assert result["counts"]["HEALTHY"] == 1


def test_case_projection_is_available_as_independent_surface():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    case = make_case(machine)

    projection = FleetOperationalProjection(
        fleet,
        cases=[case],
    )

    result = projection.case_projection()

    assert result["case_count"] == 1
    assert result["affected_machine_ids"] == ["MACHINE-001"]


def test_alert_projection_is_available_as_independent_surface():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    alert = make_alert(machine, "MEMORY_WARNING")

    projection = FleetOperationalProjection(
        fleet,
        alerts=[alert],
    )

    result = projection.alert_projection()

    assert result["alert_count"] == 1
    assert result["affected_machine_ids"] == ["MACHINE-001"]


def test_projection_is_defensive():
    fleet = Fleet("Production Fleet")
    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    projection = FleetOperationalProjection(fleet)

    result = projection.projection()
    result["inventory"]["machines"][0]["hostname"] = "TAMPERED"

    fresh = projection.projection()

    assert fresh["inventory"]["machines"][0]["hostname"] == "PC-001"


def test_external_cases_and_alerts_are_not_projected():
    fleet = Fleet("Production Fleet")

    machine = make_machine("MACHINE-001", "PC-001")
    external = make_machine("MACHINE-999", "EXTERNAL-999")

    fleet.add_machine(machine)

    fleet_case = make_case(machine)
    external_case = make_case(external)

    fleet_alert = make_alert(machine, "MEMORY_WARNING")
    external_alert = make_alert(external, "CPU_WARNING")

    projection = FleetOperationalProjection(
        fleet,
        cases=[fleet_case, external_case],
        alerts=[fleet_alert, external_alert],
    )

    result = projection.projection()

    assert result["cases"]["case_count"] == 1
    assert result["alerts"]["alert_count"] == 1


def test_empty_fleet_has_safe_operational_projection():
    fleet = Fleet("Empty Fleet")

    projection = FleetOperationalProjection(fleet)

    result = projection.projection()

    assert result["inventory"]["machines"] == []
    assert result["health"]["machine_count"] == 0
    assert result["health"]["overall_state"] == "UNKNOWN"
    assert result["cases"]["case_count"] == 0
    assert result["alerts"]["alert_count"] == 0
