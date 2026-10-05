import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession


def create_machine():
    return ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_remote_session_requires_managed_machine():
    with pytest.raises(ValueError):
        RemoteSession(None)


def test_remote_session_stores_machine():
    machine = create_machine()

    session = RemoteSession(machine)

    assert session.machine is machine


def test_remote_session_has_session_id():
    machine = create_machine()

    session = RemoteSession(machine)

    assert session.session_id is not None
    assert isinstance(session.session_id, str)
    assert session.session_id != ""


def test_remote_session_starts_disconnected():
    machine = create_machine()

    session = RemoteSession(machine)

    assert session.state == "DISCONNECTED"


def test_remote_session_can_connect():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()

    assert session.state == "CONNECTED"


def test_remote_session_can_disconnect():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"


def test_remote_session_connect_updates_machine_connection_state():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()

    assert machine.connection_state == "CONNECTED"


def test_remote_session_disconnect_updates_machine_connection_state():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"


def test_remote_session_can_connect_after_disconnect():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()
    session.disconnect()
    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_session_connect_is_idempotent():
    machine = create_machine()

    session = RemoteSession(machine)

    session.connect()
    session.connect()

    assert session.state == "CONNECTED"


def test_remote_session_disconnect_is_idempotent():
    machine = create_machine()

    session = RemoteSession(machine)

    session.disconnect()

    assert session.state == "DISCONNECTED"


def test_remote_session_does_not_own_diagnostic_case():
    machine = create_machine()

    session = RemoteSession(machine)

    assert not hasattr(session, "case")
    assert not hasattr(session, "diagnostic_case")


def test_remote_session_does_not_own_workflow():
    machine = create_machine()

    session = RemoteSession(machine)

    assert not hasattr(session, "workflow")
    assert not hasattr(session, "technician_workflow")


def test_remote_session_does_not_execute_remediation():
    machine = create_machine()

    session = RemoteSession(machine)

    assert not hasattr(session, "execute")
    assert not hasattr(session, "remediate")
    assert not hasattr(session, "remediation")