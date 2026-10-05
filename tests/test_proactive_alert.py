# ==========================================
# Windows Technician v0.8
# PROACTIVE ALERT TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
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
        message="Memory usage is significantly above baseline.",
    )


def test_proactive_alert_requires_managed_machine():
    machine = build_machine()

    alert = build_alert(machine)

    assert alert.machine is machine


def test_proactive_alert_preserves_machine_identity():
    alert = build_alert()

    assert alert.machine_id == "machine-001"
    assert alert.hostname == "REMOTE-PC"


def test_proactive_alert_preserves_alert_type():
    alert = build_alert()

    assert alert.alert_type == "ANOMALY"


def test_proactive_alert_preserves_metric():
    alert = build_alert()

    assert alert.metric == "memory_usage"


def test_proactive_alert_preserves_message():
    alert = build_alert()

    assert (
        alert.message
        == "Memory usage is significantly above baseline."
    )


def test_proactive_alert_has_active_state():
    alert = build_alert()

    assert alert.status == "ACTIVE"


def test_proactive_alert_can_be_acknowledged():
    alert = build_alert()

    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"


def test_proactive_alert_can_be_resolved():
    alert = build_alert()

    alert.resolve()

    assert alert.status == "RESOLVED"


def test_proactive_alert_can_be_dismissed():
    alert = build_alert()

    alert.dismiss()

    assert alert.status == "DISMISSED"


def test_proactive_alert_cannot_authorize_remediation():
    alert = build_alert()

    assert not hasattr(alert, "authorize")
    assert not hasattr(alert, "approve")


def test_proactive_alert_cannot_execute_remediation():
    alert = build_alert()

    assert not hasattr(alert, "execute")
    assert not hasattr(alert, "remediate")


def test_proactive_alert_does_not_contain_remediation_action():
    alert = build_alert()

    assert not hasattr(alert, "remediation_action")
    assert not hasattr(alert, "remediation_actions")


def test_proactive_alert_does_not_create_diagnostic_case():
    alert = build_alert()

    assert not hasattr(alert, "case")
    assert not hasattr(alert, "diagnostic_case")


def test_proactive_alert_does_not_create_workflow():
    alert = build_alert()

    assert not hasattr(alert, "workflow")
    assert not hasattr(alert, "technician_workflow")


def test_proactive_alert_does_not_perform_diagnosis():
    alert = build_alert()

    assert not hasattr(alert, "diagnose")
    assert not hasattr(alert, "diagnostic_pipeline")


def test_proactive_alert_does_not_retry():
    alert = build_alert()

    assert not hasattr(alert, "retry")
    assert not hasattr(alert, "retry_count")


def test_proactive_alert_does_not_recover():
    alert = build_alert()

    assert not hasattr(alert, "recover")
    assert not hasattr(alert, "recovery")


def test_proactive_alert_preserves_machine_health_state():
    machine = build_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="High memory usage.",
    )

    machine.health_state = "UNHEALTHY"

    assert machine.health_state == "UNHEALTHY"
    assert alert.machine is machine


def test_proactive_alert_preserves_connection_state():
    machine = build_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="High memory usage.",
    )

    machine.connection_state = "CONNECTED"

    assert machine.connection_state == "CONNECTED"
    assert alert.machine is machine


def test_proactive_alert_is_machine_specific():
    machine_a = build_machine()

    machine_b = ManagedMachine(
        machine_id="machine-002",
        hostname="SECOND-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    alert_a = ProactiveAlert(
        machine=machine_a,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="High memory usage.",
    )

    alert_b = ProactiveAlert(
        machine=machine_b,
        alert_type="TREND",
        metric="cpu_usage",
        message="CPU usage is increasing.",
    )

    assert alert_a.machine_id != alert_b.machine_id
    assert alert_a.hostname != alert_b.hostname


def test_proactive_alert_status_is_not_execution_status():
    alert = build_alert()

    assert alert.status == "ACTIVE"
    assert not hasattr(alert, "execution_status")


def test_proactive_alert_status_is_not_authorization_status():
    alert = build_alert()

    assert alert.status == "ACTIVE"
    assert not hasattr(alert, "authorization_status")


def test_proactive_alert_does_not_equal_remediation():
    alert = build_alert()

    assert not hasattr(alert, "operation")
    assert not hasattr(alert, "handler")


def test_proactive_alert_does_not_equal_diagnosis():
    alert = build_alert()

    assert alert.alert_type == "ANOMALY"
    assert not hasattr(alert, "findings")
    assert not hasattr(alert, "root_causes")


def test_proactive_alert_is_an_observation_output():
    alert = build_alert()

    assert alert.machine_id is not None
    assert alert.alert_type is not None
    assert alert.metric is not None
    assert alert.message is not None
    assert alert.status == "ACTIVE"