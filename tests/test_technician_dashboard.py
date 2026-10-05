# ==========================================
# Windows Technician v0.8
# TECHNICIAN DASHBOARD TESTS
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


def build_alert(machine=None):
    if machine is None:
        machine = build_machine()

    return ProactiveAlert(
        machine=machine,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="Memory usage is above baseline.",
    )


def build_recommendation(alert=None):
    if alert is None:
        alert = build_alert()

    return ProactiveRecommendation(
        alert=alert,
        recommendation="Review memory usage.",
    )


def build_case(machine=None):
    if machine is None:
        machine = build_machine()

    alert = build_alert(machine)
    recommendation = build_recommendation(alert)

    return ProactiveCaseCreator().create(
        recommendation
    )


def test_technician_dashboard_module_exists():
    from engine.technician_dashboard import TechnicianDashboard

    assert TechnicianDashboard is not None


def test_technician_dashboard_can_be_created():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert dashboard is not None


def test_dashboard_starts_with_no_machines():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert dashboard.machines == []


def test_dashboard_starts_with_no_alerts():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert dashboard.alerts == []


def test_dashboard_starts_with_no_cases():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert dashboard.cases == []


def test_dashboard_can_add_machine():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    machine = build_machine()

    dashboard.add_machine(machine)

    assert dashboard.machines == [machine]


def test_dashboard_rejects_invalid_machine():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    try:
        dashboard.add_machine(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid machine should raise ValueError."
        )


def test_dashboard_can_add_alert():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    alert = build_alert()

    dashboard.add_alert(alert)

    assert dashboard.alerts == [alert]


def test_dashboard_rejects_invalid_alert():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    try:
        dashboard.add_alert(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid alert should raise ValueError."
        )


def test_dashboard_can_add_case():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    case = build_case()

    dashboard.add_case(case)

    assert dashboard.cases == [case]


def test_dashboard_rejects_invalid_case():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    try:
        dashboard.add_case(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid case should raise ValueError."
        )


def test_dashboard_preserves_machine_identity():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    machine = build_machine()

    dashboard.add_machine(machine)

    assert dashboard.machines[0] is machine


def test_dashboard_preserves_alert_identity():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    alert = build_alert()

    dashboard.add_alert(alert)

    assert dashboard.alerts[0] is alert


def test_dashboard_preserves_case_identity():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    case = build_case()

    dashboard.add_case(case)

    assert dashboard.cases[0] is case


def test_dashboard_can_hold_multiple_machines():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    machine_one = build_machine(
        "machine-001",
        "PC-ONE",
    )
    machine_two = build_machine(
        "machine-002",
        "PC-TWO",
    )

    dashboard.add_machine(machine_one)
    dashboard.add_machine(machine_two)

    assert dashboard.machines == [
        machine_one,
        machine_two,
    ]


def test_dashboard_can_hold_multiple_alerts():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    alert_one = build_alert(
        build_machine("machine-001", "PC-ONE")
    )
    alert_two = build_alert(
        build_machine("machine-002", "PC-TWO")
    )

    dashboard.add_alert(alert_one)
    dashboard.add_alert(alert_two)

    assert dashboard.alerts == [
        alert_one,
        alert_two,
    ]


def test_dashboard_can_hold_multiple_cases():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    case_one = build_case(
        build_machine("machine-001", "PC-ONE")
    )
    case_two = build_case(
        build_machine("machine-002", "PC-TWO")
    )

    dashboard.add_case(case_one)
    dashboard.add_case(case_two)

    assert dashboard.cases == [
        case_one,
        case_two,
    ]


def test_dashboard_exposes_machine_count():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    dashboard.add_machine(build_machine())

    assert dashboard.machine_count == 1


def test_dashboard_exposes_alert_count():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    dashboard.add_alert(build_alert())

    assert dashboard.alert_count == 1


def test_dashboard_exposes_case_count():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    dashboard.add_case(build_case())

    assert dashboard.case_count == 1


def test_dashboard_is_read_oriented():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert not hasattr(dashboard, "diagnose")
    assert not hasattr(dashboard, "execute")
    assert not hasattr(dashboard, "remediate")
    assert not hasattr(dashboard, "authorize")


def test_dashboard_does_not_create_remediation():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert not hasattr(
        dashboard,
        "remediation_action",
    )
    assert not hasattr(
        dashboard,
        "remediation_actions",
    )


def test_dashboard_does_not_create_workflow():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    assert not hasattr(
        dashboard,
        "technician_workflow",
    )


def test_dashboard_does_not_mutate_machine():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    machine = build_machine()

    original_connection_state = (
        machine.connection_state
    )
    original_health_state = machine.health_state

    dashboard.add_machine(machine)

    assert machine.connection_state == (
        original_connection_state
    )
    assert machine.health_state == (
        original_health_state
    )


def test_dashboard_does_not_mutate_alert():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    alert = build_alert()

    original_status = alert.status

    dashboard.add_alert(alert)

    assert alert.status == original_status


def test_dashboard_does_not_mutate_case():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()
    case = build_case()

    original_state = case.lifecycle_state

    dashboard.add_case(case)

    assert case.lifecycle_state == original_state


def test_dashboard_supports_machine_specific_alerts():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    machine_one = build_machine(
        "machine-001",
        "PC-ONE",
    )
    machine_two = build_machine(
        "machine-002",
        "PC-TWO",
    )

    alert_one = build_alert(machine_one)
    alert_two = build_alert(machine_two)

    dashboard.add_machine(machine_one)
    dashboard.add_machine(machine_two)

    dashboard.add_alert(alert_one)
    dashboard.add_alert(alert_two)

    assert dashboard.alerts[0].machine_id == (
        machine_one.machine_id
    )
    assert dashboard.alerts[1].machine_id == (
        machine_two.machine_id
    )


def test_dashboard_supports_machine_specific_cases():
    from engine.technician_dashboard import TechnicianDashboard

    dashboard = TechnicianDashboard()

    machine_one = build_machine(
        "machine-001",
        "PC-ONE",
    )
    machine_two = build_machine(
        "machine-002",
        "PC-TWO",
    )

    case_one = build_case(machine_one)
    case_two = build_case(machine_two)

    dashboard.add_machine(machine_one)
    dashboard.add_machine(machine_two)

    dashboard.add_case(case_one)
    dashboard.add_case(case_two)

    assert dashboard.cases[0].machine_id == (
        machine_one.machine_id
    )
    assert dashboard.cases[1].machine_id == (
        machine_two.machine_id
    )