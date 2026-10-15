from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_workspace import FleetWorkspace
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


def make_case(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    return case


def make_alert(machine, alert_type):
    return ProactiveAlert(
        machine=machine,
        alert_type=alert_type,
        metric="memory",
        message="Memory usage requires attention.",
    )


def test_workspace_requires_canonical_fleet():
    try:
        FleetWorkspace(None)
    except ValueError as exc:
        assert "Fleet" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_workspace_exposes_fleet_identity():
    fleet = Fleet("Production Fleet")

    workspace = FleetWorkspace(fleet)

    assert workspace.fleet_id == fleet.fleet_id
    assert workspace.fleet_name == "Production Fleet"


def test_workspace_composes_operational_surfaces():
    fleet = Fleet("Production Fleet")

    machine = make_machine(
        "MACHINE-001",
        "PC-001",
        health_state="HEALTHY",
    )
    fleet.add_machine(machine)

    case = make_case(machine)
    alert = make_alert(machine, "MEMORY_WARNING")

    workspace = FleetWorkspace(
        fleet,
        cases=[case],
        alerts=[alert],
    )

    projection = workspace.workspace_projection()

    assert set(projection) == {
        "fleet",
        "inventory",
        "health",
        "cases",
        "alerts",
    }

    assert projection["fleet"]["name"] == "Production Fleet"
    assert projection["inventory"]["machines"][0]["machine_id"] == (
        "MACHINE-001"
    )
    assert projection["health"]["overall_state"] == "HEALTHY"
    assert projection["cases"]["case_count"] == 1
    assert projection["alerts"]["alert_count"] == 1


def test_workspace_exposes_individual_surfaces():
    fleet = Fleet("Production Fleet")

    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    workspace = FleetWorkspace(fleet)

    assert workspace.machine_inventory()["machines"][0]["hostname"] == (
        "PC-001"
    )

    assert workspace.health()["machine_count"] == 1
    assert workspace.cases()["case_count"] == 0
    assert workspace.alerts()["alert_count"] == 0


def test_workspace_projection_is_defensive():
    fleet = Fleet("Production Fleet")

    machine = make_machine("MACHINE-001", "PC-001")
    fleet.add_machine(machine)

    workspace = FleetWorkspace(fleet)

    projection = workspace.workspace_projection()
    projection["inventory"]["machines"][0]["hostname"] = "TAMPERED"

    fresh = workspace.workspace_projection()

    assert fresh["inventory"]["machines"][0]["hostname"] == "PC-001"


def test_workspace_preserves_fleet_membership_boundary():
    fleet = Fleet("Production Fleet")

    machine = make_machine("MACHINE-001", "PC-001")
    external = make_machine("MACHINE-999", "EXTERNAL-999")

    fleet.add_machine(machine)

    fleet_case = make_case(machine)
    external_case = make_case(external)

    fleet_alert = make_alert(machine, "MEMORY_WARNING")
    external_alert = make_alert(external, "CPU_WARNING")

    workspace = FleetWorkspace(
        fleet,
        cases=[fleet_case, external_case],
        alerts=[fleet_alert, external_alert],
    )

    projection = workspace.workspace_projection()

    assert projection["cases"]["case_count"] == 1
    assert projection["alerts"]["alert_count"] == 1


def test_empty_fleet_workspace_is_safe():
    fleet = Fleet("Empty Fleet")

    workspace = FleetWorkspace(fleet)

    projection = workspace.workspace_projection()

    assert projection["inventory"]["machines"] == []
    assert projection["health"]["machine_count"] == 0
    assert projection["health"]["overall_state"] == "UNKNOWN"
    assert projection["cases"]["case_count"] == 0
    assert projection["alerts"]["alert_count"] == 0
