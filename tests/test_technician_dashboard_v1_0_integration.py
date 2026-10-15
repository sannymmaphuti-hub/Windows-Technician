from engine.case_queue import CaseQueue
from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_dashboard import TechnicianDashboard
from engine.technician_workflow import TechnicianWorkflow


def make_machine(
    machine_id="machine-1",
    hostname="TEST-PC",
):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="WINDOWS",
        operating_system="Windows 11",
    )


def make_case(
    machine_id="machine-1",
    hostname="TEST-PC",
):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = hostname
    return case


def test_dashboard_composes_canonical_machine_health():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    machine.connection_state = "CONNECTED"
    machine.health_state = "HEALTHY"

    dashboard.add_machine(machine)

    assert dashboard.machine_health() == [
        {
            "machine_id": "machine-1",
            "hostname": "TEST-PC",
            "connection_state": "CONNECTED",
            "health_state": "HEALTHY",
            "last_seen": None,
        }
    ]


def test_dashboard_composes_canonical_fleet_alerts():
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

    assert dashboard.fleet_alerts()[0]["machine_id"] == "machine-1"
    assert dashboard.fleet_alerts()[0]["status"] == "ACTIVE"


def test_dashboard_uses_case_queue_for_active_cases():
    dashboard = TechnicianDashboard()
    queue = CaseQueue()

    case = make_case()
    queue.add_case(case)

    dashboard.set_case_queue(queue)

    active = dashboard.active_cases()

    assert len(active) == 1
    assert active[0]["case_id"] == case.case_id
    assert active[0]["lifecycle_state"] == "OPEN"


def test_dashboard_reports_unresolved_cases_without_deciding_remediation():
    dashboard = TechnicianDashboard()
    case = make_case()

    dashboard.add_case(case)

    unresolved = dashboard.unresolved_problems()

    assert len(unresolved) == 1
    assert unresolved[0]["case_id"] == case.case_id


def test_dashboard_composes_canonical_fleet_membership():
    dashboard = TechnicianDashboard()
    fleet = Fleet("Production")

    fleet.add_machine(make_machine())

    dashboard.add_fleet(fleet)

    assert dashboard.fleet_count == 1
    assert dashboard.fleets[0] is fleet


def test_dashboard_composes_activity_log():
    dashboard = TechnicianDashboard()
    case = make_case()

    workflow = TechnicianWorkflow(case)
    activity = TechnicianActivityLog(workflow)

    workflow.start_investigation()
    activity.record_workflow_event()

    dashboard.add_activity_log(activity)

    entries = dashboard.recent_activity()

    assert len(entries) == 1
    assert entries[0]["type"] == "WORKFLOW"


def test_dashboard_projection_is_presentation_only():
    dashboard = TechnicianDashboard()

    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert not forbidden.intersection(
        dir(dashboard)
    )


def test_dashboard_projection_is_defensive():
    dashboard = TechnicianDashboard()
    machine = make_machine()

    dashboard.add_machine(machine)

    projection = dashboard.dashboard_projection()

    projection["machine_health"][0]["health_state"] = "CORRUPTED"

    assert (
        dashboard.machine_health()[0]["health_state"]
        == "UNKNOWN"
    )
