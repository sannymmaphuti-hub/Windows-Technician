from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession


def create_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="TECH-PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_remote_management_starts_with_unavailable_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    assert machine.is_available is False
    assert machine.connection_state == "UNKNOWN"
    assert session.state == "DISCONNECTED"


def test_remote_management_connects_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True


def test_remote_management_disconnects_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"
    assert machine.is_available is False


def test_remote_management_can_reconnect():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()
    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True


def test_failed_connection_makes_machine_unavailable():
    machine = create_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert session.state == "FAILED"
    assert machine.is_available is False


def test_failed_connection_can_recover_to_connected():
    machine = create_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"
    assert machine.is_available is True


def test_session_identity_is_unique_per_session():
    machine = create_machine()

    session_one = RemoteSession(machine)
    session_two = RemoteSession(machine)

    assert session_one.session_id != session_two.session_id


def test_multiple_sessions_reference_same_machine():
    machine = create_machine()

    session_one = RemoteSession(machine)
    session_two = RemoteSession(machine)

    assert session_one.machine is machine
    assert session_two.machine is machine
    assert session_one.machine.machine_id == "machine-001"
    assert session_two.machine.machine_id == "machine-001"


def test_machine_identity_survives_connection_lifecycle():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()
    session.connect()

    assert machine.machine_id == "machine-001"
    assert machine.hostname == "TECH-PC-01"
    assert machine.platform == "Windows"
    assert machine.operating_system == "Windows 11"


def test_remote_management_does_not_create_workflow():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert not hasattr(machine, "workflow")
    assert not hasattr(session, "workflow")


def test_remote_management_does_not_create_diagnostic_case():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert not hasattr(machine, "case")
    assert not hasattr(session, "case")


def test_remote_management_does_not_execute_remediation():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert not hasattr(session, "execute")
    assert not hasattr(session, "remediate")