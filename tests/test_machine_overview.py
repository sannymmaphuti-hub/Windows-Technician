# ==========================================
# Windows Technician v0.8
# MACHINE OVERVIEW TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.proactive_recommendation import ProactiveRecommendation


def build_machine(
    machine_id="machine-001",
    hostname="TECH-PC",
):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="Windows",
        operating_system="Windows 11",
    )


def build_alert(machine):
    return ProactiveAlert(
        machine=machine,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="Memory usage is above baseline.",
    )


def build_case(machine):
    alert = build_alert(machine)

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Review memory usage.",
    )

    return ProactiveCaseCreator().create(
        recommendation
    )


def test_machine_overview_module_exists():
    from engine.machine_overview import MachineOverview

    assert MachineOverview is not None


def test_machine_overview_requires_managed_machine():
    from engine.machine_overview import MachineOverview

    try:
        MachineOverview(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "MachineOverview should require ManagedMachine."
        )


def test_machine_overview_preserves_machine_identity():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.machine is machine


def test_machine_overview_exposes_machine_id():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.machine_id == machine.machine_id


def test_machine_overview_exposes_hostname():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.hostname == machine.hostname


def test_machine_overview_exposes_platform():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.platform == machine.platform


def test_machine_overview_exposes_operating_system():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.operating_system == (
        machine.operating_system
    )


def test_machine_overview_exposes_connection_state():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    machine.connection_state = "CONNECTED"

    overview = MachineOverview(machine)

    assert overview.connection_state == "CONNECTED"


def test_machine_overview_exposes_health_state():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    machine.health_state = "HEALTHY"

    overview = MachineOverview(machine)

    assert overview.health_state == "HEALTHY"


def test_machine_overview_exposes_last_seen():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    machine.last_seen = "2026-10-05T10:00:00"

    overview = MachineOverview(machine)

    assert overview.last_seen == machine.last_seen


def test_machine_overview_starts_without_alerts():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.alerts == []


def test_machine_overview_starts_without_cases():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    overview = MachineOverview(machine)

    assert overview.cases == []


def test_machine_overview_can_add_alert():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    alert = build_alert(machine)

    overview = MachineOverview(machine)
    overview.add_alert(alert)

    assert overview.alerts == [alert]


def test_machine_overview_rejects_alert_from_wrong_machine():
    from engine.machine_overview import MachineOverview

    machine_one = build_machine(
        "machine-001",
        "PC-ONE",
    )
    machine_two = build_machine(
        "machine-002",
        "PC-TWO",
    )

    alert = build_alert(machine_two)

    overview = MachineOverview(machine_one)

    try:
        overview.add_alert(alert)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Alert from another machine should be rejected."
        )


def test_machine_overview_can_add_case():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    case = build_case(machine)

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert overview.cases == [case]


def test_machine_overview_rejects_case_from_wrong_machine():
    from engine.machine_overview import MachineOverview

    machine_one = build_machine(
        "machine-001",
        "PC-ONE",
    )
    machine_two = build_machine(
        "machine-002",
        "PC-TWO",
    )

    case = build_case(machine_two)

    overview = MachineOverview(machine_one)

    try:
        overview.add_case(case)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Case from another machine should be rejected."
        )


def test_machine_overview_preserves_alert_identity():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    alert = build_alert(machine)

    overview = MachineOverview(machine)
    overview.add_alert(alert)

    assert overview.alerts[0] is alert


def test_machine_overview_preserves_case_identity():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    case = build_case(machine)

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert overview.cases[0] is case


def test_machine_overview_does_not_diagnose():
    from engine.machine_overview import MachineOverview

    overview = MachineOverview(build_machine())

    assert not hasattr(overview, "diagnose")
    assert not hasattr(overview, "diagnostic_pipeline")


def test_machine_overview_does_not_authorize():
    from engine.machine_overview import MachineOverview

    overview = MachineOverview(build_machine())

    assert not hasattr(overview, "authorize")
    assert not hasattr(overview, "authorization_status")


def test_machine_overview_does_not_execute():
    from engine.machine_overview import MachineOverview

    overview = MachineOverview(build_machine())

    assert not hasattr(overview, "execute")
    assert not hasattr(overview, "execution_status")


def test_machine_overview_does_not_remediate():
    from engine.machine_overview import MachineOverview

    overview = MachineOverview(build_machine())

    assert not hasattr(overview, "remediate")
    assert not hasattr(overview, "remediation_action")
    assert not hasattr(overview, "remediation_actions")


def test_machine_overview_does_not_create_workflow():
    from engine.machine_overview import MachineOverview

    overview = MachineOverview(build_machine())

    assert not hasattr(overview, "workflow")
    assert not hasattr(overview, "technician_workflow")


def test_machine_overview_does_not_mutate_machine():
    from engine.machine_overview import MachineOverview

    machine = build_machine()

    original_connection = machine.connection_state
    original_health = machine.health_state
    original_last_seen = machine.last_seen

    MachineOverview(machine)

    assert machine.connection_state == original_connection
    assert machine.health_state == original_health
    assert machine.last_seen == original_last_seen


def test_machine_overview_exposes_alert_count():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    overview = MachineOverview(machine)

    overview.add_alert(build_alert(machine))
    overview.add_alert(build_alert(machine))

    assert overview.alert_count == 2


def test_machine_overview_exposes_case_count():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    overview = MachineOverview(machine)

    overview.add_case(build_case(machine))
    overview.add_case(build_case(machine))

    assert overview.case_count == 2


def test_machine_overview_is_machine_specific():
    from engine.machine_overview import MachineOverview

    machine = build_machine(
        "machine-123",
        "CUSTOM-PC",
    )

    overview = MachineOverview(machine)

    assert overview.machine_id == "machine-123"
    assert overview.hostname == "CUSTOM-PC"


def test_machine_overview_uses_existing_case_model():
    from engine.machine_overview import MachineOverview

    machine = build_machine()
    case = build_case(machine)

    overview = MachineOverview(machine)
    overview.add_case(case)

    assert type(overview.cases[0]) is DiagnosticCase