import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext


def create_machine(machine_id="machine-001"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname="TECH-PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_remote_diagnostic_context_requires_machine():
    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=None,
            session=None,
        )


def test_remote_diagnostic_context_requires_session():
    machine = create_machine()

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session=None,
        )


def test_remote_diagnostic_context_requires_remote_session():
    machine = create_machine()

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session="not-a-session",
        )


def test_remote_diagnostic_context_requires_matching_machine():
    machine_one = create_machine("machine-001")
    machine_two = create_machine("machine-002")

    session = RemoteSession(machine_one)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_two,
            session=session,
        )


def test_remote_diagnostic_context_requires_available_session():
    machine = create_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session=session,
        )


def test_remote_diagnostic_context_stores_machine():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.machine is machine


def test_remote_diagnostic_context_stores_session():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.session is session


def test_remote_diagnostic_context_exposes_machine_identity():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.machine_id == "machine-001"
    assert context.hostname == "TECH-PC-01"


def test_remote_diagnostic_context_exposes_session_identity():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.session_id == session.session_id


def test_remote_diagnostic_context_is_remote():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.is_remote is True


def test_remote_diagnostic_context_does_not_create_case():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert not hasattr(context, "case")
    assert not hasattr(context, "diagnostic_case")
    assert not hasattr(context, "create_case")


def test_remote_diagnostic_context_does_not_create_workflow():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert not hasattr(context, "workflow")
    assert not hasattr(context, "technician_workflow")


def test_remote_diagnostic_context_does_not_execute_remediation():
    machine = create_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert not hasattr(context, "execute")
    assert not hasattr(context, "remediate")
    assert not hasattr(context, "remediation")