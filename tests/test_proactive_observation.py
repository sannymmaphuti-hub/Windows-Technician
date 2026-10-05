# ==========================================
# Windows Technician v0.8
# PROACTIVE OBSERVATION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_managed_machine_can_exist_as_observation_source():
    machine = build_machine()

    assert machine.machine_id == "machine-001"
    assert machine.hostname == "REMOTE-PC"


def test_machine_identity_is_stable_for_observation():
    machine = build_machine()

    machine_id = machine.machine_id

    assert machine.machine_id == machine_id


def test_machine_health_state_exists_for_proactive_monitoring():
    machine = build_machine()

    assert hasattr(machine, "health_state")
    assert machine.health_state == "UNKNOWN"


def test_machine_connection_state_exists_for_proactive_monitoring():
    machine = build_machine()

    assert hasattr(machine, "connection_state")
    assert machine.connection_state == "UNKNOWN"


def test_proactive_monitoring_must_not_change_machine_identity():
    machine = build_machine()

    machine_id = machine.machine_id
    hostname = machine.hostname

    assert machine.machine_id == machine_id
    assert machine.hostname == hostname


def test_proactive_monitoring_does_not_authorize_remediation():
    machine = build_machine()

    assert not hasattr(machine, "authorize")
    assert not hasattr(machine, "approve")


def test_proactive_monitoring_does_not_execute_remediation():
    machine = build_machine()

    assert not hasattr(machine, "execute")
    assert not hasattr(machine, "remediate")


def test_proactive_monitoring_does_not_create_remediation_action():
    machine = build_machine()

    assert not hasattr(machine, "remediation_action")
    assert not hasattr(machine, "remediation_actions")


def test_proactive_monitoring_does_not_create_diagnostic_case():
    machine = build_machine()

    assert not hasattr(machine, "case")
    assert not hasattr(machine, "diagnostic_case")


def test_proactive_monitoring_does_not_create_alert_implicitly():
    machine = build_machine()

    assert not hasattr(machine, "alert")
    assert not hasattr(machine, "proactive_alert")


def test_machine_can_represent_healthy_state():
    machine = build_machine()

    machine.health_state = "HEALTHY"

    assert machine.health_state == "HEALTHY"


def test_machine_can_represent_unhealthy_state():
    machine = build_machine()

    machine.health_state = "UNHEALTHY"

    assert machine.health_state == "UNHEALTHY"


def test_health_state_is_distinct_from_connection_state():
    machine = build_machine()

    machine.connection_state = "CONNECTED"
    machine.health_state = "UNHEALTHY"

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "UNHEALTHY"


def test_proactive_observation_does_not_equal_remediation():
    machine = build_machine()

    machine.health_state = "UNHEALTHY"

    assert machine.health_state == "UNHEALTHY"
    assert not hasattr(machine, "execute")


def test_proactive_observation_does_not_equal_authorization():
    machine = build_machine()

    machine.health_state = "UNHEALTHY"

    assert not hasattr(machine, "authorize")


def test_proactive_monitoring_preserves_platform_information():
    machine = build_machine()

    assert machine.platform == "Windows"
    assert machine.operating_system == "Windows 11"


def test_proactive_monitoring_preserves_hostname():
    machine = build_machine()

    assert machine.hostname == "REMOTE-PC"


def test_proactive_monitoring_has_no_hidden_retry_behavior():
    machine = build_machine()

    assert not hasattr(machine, "retry")
    assert not hasattr(machine, "retry_count")


def test_proactive_monitoring_has_no_hidden_recovery_behavior():
    machine = build_machine()

    assert not hasattr(machine, "recover")
    assert not hasattr(machine, "recovery")


def test_proactive_monitoring_is_not_a_replacement_for_existing_diagnostic_pipeline():
    machine = build_machine()

    assert not hasattr(machine, "diagnose")
    assert not hasattr(machine, "diagnostic_pipeline")


def test_proactive_monitoring_is_not_a_replacement_for_existing_workflow():
    machine = build_machine()

    assert not hasattr(machine, "workflow")
    assert not hasattr(machine, "technician_workflow")


def test_machine_is_suitable_as_canonical_proactive_observation_owner():
    machine = build_machine()

    assert machine.machine_id is not None
    assert machine.hostname is not None
    assert machine.platform is not None
    assert machine.operating_system is not None