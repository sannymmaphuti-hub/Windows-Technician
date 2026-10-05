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


def test_session_starts_disconnected():
    session = RemoteSession(create_machine())

    assert session.state == "DISCONNECTED"


def test_session_connects():
    session = RemoteSession(create_machine())

    session.connect()

    assert session.state == "CONNECTED"


def test_session_disconnects():
    session = RemoteSession(create_machine())

    session.connect()
    session.disconnect()

    assert session.state == "DISCONNECTED"


def test_connecting_state_can_be_set():
    session = RemoteSession(create_machine())

    session.state = "CONNECTING"

    assert session.state == "CONNECTING"


def test_failed_state_can_be_set():
    session = RemoteSession(create_machine())

    session.state = "FAILED"

    assert session.state == "FAILED"


def test_failed_session_can_reconnect():
    session = RemoteSession(create_machine())

    session.state = "FAILED"
    session.connect()

    assert session.state == "CONNECTED"


def test_connect_updates_machine_state():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert machine.connection_state == "CONNECTED"


def test_disconnect_updates_machine_state():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"


def test_failed_session_does_not_report_machine_as_connected():
    machine = create_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert session.state == "FAILED"
    assert machine.connection_state == "FAILED"


def test_session_has_no_diagnostic_responsibility():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "diagnose")
    assert not hasattr(session, "diagnostic_case")


def test_session_has_no_remediation_responsibility():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "execute")
    assert not hasattr(session, "remediate")
    assert not hasattr(session, "remediation")