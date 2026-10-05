# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION CONTEXT TESTS
# ==========================================

import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_remediation_context import RemoteRemediationContext


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_connected_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def test_remote_remediation_context_requires_machine():
    with pytest.raises(ValueError):
        RemoteRemediationContext(
            None,
            None,
        )


def test_remote_remediation_context_requires_session():
    machine = build_machine()

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine,
            None,
        )


def test_remote_remediation_context_requires_matching_session():
    machine_one = build_machine()

    machine_two = ManagedMachine(
        machine_id="machine-002",
        hostname="OTHER-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = build_connected_session(machine_one)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine_two,
            session,
        )


def test_remote_remediation_context_requires_available_machine():
    machine = build_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine,
            session,
        )


def test_remote_remediation_context_accepts_connected_machine():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert context.machine is machine
    assert context.session is session


def test_machine_identity_is_preserved():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert context.machine_id == "machine-001"
    assert context.hostname == "REMOTE-PC"


def test_session_identity_is_preserved():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert context.session_id == session.session_id


def test_context_is_remote():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert context.is_remote is True


def test_context_does_not_create_diagnostic_case():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert not hasattr(context, "case")


def test_context_does_not_create_technician_workflow():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert not hasattr(context, "workflow")


def test_context_does_not_execute_remediation():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert not hasattr(context, "execute")
    assert not hasattr(context, "execute_remediation")


def test_context_does_not_authorize_remediation():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    assert not hasattr(context, "authorize")
    assert not hasattr(context, "approve")