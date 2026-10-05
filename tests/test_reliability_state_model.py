# ==========================================
# Windows Technician v0.8
# RELIABILITY STATE MODEL TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_new_remote_session_starts_disconnected():
    machine = build_machine()
    session = RemoteSession(machine)

    assert session.state == "DISCONNECTED"


def test_connected_session_has_connected_state():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()

    assert session.state == "CONNECTED"


def test_disconnect_changes_session_state():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"


def test_connection_failure_is_distinct_from_disconnection():
    machine = build_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert session.state == "FAILED"
    assert machine.connection_state == "FAILED"
    assert session.state != "DISCONNECTED"


def test_connecting_is_distinct_from_connected():
    machine = build_machine()
    session = RemoteSession(machine)

    session.state = "CONNECTING"
    machine.connection_state = "CONNECTING"

    assert session.state == "CONNECTING"
    assert machine.connection_state == "CONNECTING"
    assert session.state != "CONNECTED"


def test_connection_loss_does_not_mean_remediation_failure():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert session.state != "FAILED"


def test_failed_connection_does_not_mean_machine_is_available():
    machine = build_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert machine.is_available is False


def test_connecting_machine_is_not_available():
    machine = build_machine()
    session = RemoteSession(machine)

    session.state = "CONNECTING"
    machine.connection_state = "CONNECTING"

    assert machine.is_available is False


def test_disconnected_machine_is_not_available():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert machine.is_available is False


def test_connected_machine_is_available():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()

    assert machine.is_available is True


def test_reconnection_restores_availability():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert machine.is_available is False

    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True


def test_connection_state_does_not_change_health_state():
    machine = build_machine()
    session = RemoteSession(machine)

    machine.health_state = "UNHEALTHY"

    session.connect()

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "UNHEALTHY"

    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"
    assert machine.health_state == "UNHEALTHY"


def test_reliability_state_does_not_create_diagnostic_case():
    machine = build_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert not hasattr(session, "case")
    assert not hasattr(session, "diagnostic_case")


def test_reliability_state_does_not_create_recovery_workflow():
    machine = build_machine()
    session = RemoteSession(machine)

    assert not hasattr(session, "recover")
    assert not hasattr(session, "retry")
    assert not hasattr(session, "reinvestigate")


def test_session_identity_survives_connection_changes():
    machine = build_machine()
    session = RemoteSession(machine)

    session_id = session.session_id

    session.connect()
    session.disconnect()
    session.connect()

    assert session.session_id == session_id


def test_machine_identity_survives_connection_changes():
    machine = build_machine()
    session = RemoteSession(machine)

    machine_id = machine.machine_id

    session.connect()
    session.disconnect()
    session.connect()

    assert machine.machine_id == machine_id