from engine.dashboard_view_model import DashboardViewModel
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.technician_dashboard import TechnicianDashboard


class ApplicationStateStub:
    active_machine_id = "MACHINE-1"
    active_case_id = "CASE-1"


def make_machine():
    return ManagedMachine(
        machine_id="machine-1",
        hostname="TEST-PC",
        platform="WINDOWS",
        operating_system="Windows 11",
    )


def test_view_model_binds_canonical_technician_dashboard():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    machine.connection_state = "CONNECTED"
    machine.health_state = "HEALTHY"

    dashboard.add_machine(machine)

    view_model = DashboardViewModel(ApplicationStateStub())

    view_model.bind_dashboard(dashboard)

    assert view_model.active_cases() == []
    assert view_model.fleet_alerts() == []
    assert view_model.unresolved_problems() == []
    assert view_model.remediation_status() == []
    assert view_model.verification_status() == []
    assert view_model.recent_activity() == []


def test_view_model_receives_fleet_alert_projection():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_PRESSURE",
        metric="RAM",
        message="Memory pressure detected.",
    )

    dashboard.add_machine(machine)
    dashboard.add_alert(alert)

    view_model = DashboardViewModel(ApplicationStateStub())
    view_model.bind_dashboard(dashboard)

    alerts = view_model.fleet_alerts()

    assert len(alerts) == 1
    assert alerts[0]["machine_id"] == "machine-1"
    assert alerts[0]["status"] == "ACTIVE"


def test_view_model_dashboard_projection_is_defensive():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    dashboard.add_machine(machine)

    view_model = DashboardViewModel(ApplicationStateStub())
    view_model.bind_dashboard(dashboard)

    projection = view_model.to_dict()

    projection["fleet_alerts"].append(
        {"machine_id": "corrupted"}
    )

    assert view_model.fleet_alerts() == []


def test_view_model_clear_dashboard_removes_operational_projection():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_PRESSURE",
        metric="CPU",
        message="CPU pressure detected.",
    )

    dashboard.add_machine(machine)
    dashboard.add_alert(alert)

    view_model = DashboardViewModel(ApplicationStateStub())
    view_model.bind_dashboard(dashboard)

    assert len(view_model.fleet_alerts()) == 1

    view_model.clear_dashboard()

    assert view_model.fleet_alerts() == []
    assert view_model.active_cases() == []
    assert view_model.unresolved_problems() == []
    assert view_model.remediation_status() == []
    assert view_model.verification_status() == []
    assert view_model.recent_activity() == []


def test_view_model_preserves_existing_intelligence_contract():
    view_model = DashboardViewModel(
        ApplicationStateStub(),
        intelligence={
            "health": {
                "status": "WARNING",
                "score": 72,
            },
            "system_findings": [{"id": "finding-1"}],
            "relationships": [{"id": "relationship-1"}],
            "root_causes": [{"id": "root-1"}],
            "recommendations": [{"id": "recommendation-1"}],
        },
    )

    assert view_model.summary() == {
        "status": "WARNING",
        "health_score": 72,
        "finding_count": 1,
        "relationship_count": 1,
        "root_cause_count": 1,
        "recommendation_count": 1,
        "machine_id": "MACHINE-1",
        "case_id": "CASE-1",
    }
