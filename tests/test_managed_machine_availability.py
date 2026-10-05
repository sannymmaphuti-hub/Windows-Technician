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


def test_machine_is_unavailable_when_not_connected():
    machine = create_machine()

    assert machine.is_available is False


def test_machine_is_available_when_connected():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert machine.is_available is True


def test_machine_becomes_unavailable_after_disconnect():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    session.disconnect()

    assert machine.is_available is False


def test_machine_is_unavailable_when_connection_failed():
    machine = create_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert machine.is_available is False


def test_machine_is_unavailable_while_connecting():
    machine = create_machine()
    session = RemoteSession(machine)

    session.state = "CONNECTING"
    machine.connection_state = "CONNECTING"

    assert machine.is_available is False


def test_availability_does_not_require_health_state():
    machine = create_machine()
    session = RemoteSession(machine)

    machine.health_state = "UNKNOWN"
    session.connect()

    assert machine.is_available is True


def test_unhealthy_machine_can_still_be_available():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()
    machine.health_state = "UNHEALTHY"

    assert machine.is_available is True


def test_availability_is_derived_from_connection_state():
    machine = create_machine()

    machine.connection_state = "CONNECTED"

    assert machine.is_available is True


def test_unknown_connection_state_means_unavailable():
    machine = create_machine()

    machine.connection_state = "UNKNOWN"

    assert machine.is_available is False