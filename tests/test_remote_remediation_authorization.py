# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION AUTHORIZATION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remediation_action import RemediationAction


def build_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    return RemoteRemediationContext(
        machine,
        session,
    )


def build_action():
    return RemediationAction(
        action_id="remote-action-001",
        description="Review high memory usage",
        category="MEMORY",
        severity="HIGH",
    )


def test_remote_context_can_be_created_for_authorization():
    context = build_context()

    assert context.is_remote is True
    assert context.machine_id == "machine-001"


def test_remote_remediation_action_starts_unauthorized():
    action = build_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_remote_remediation_requires_explicit_authorization():
    action = build_action()

    assert action.requires_authorization is True
    assert action.authorization_status != "AUTHORIZED"


def test_remote_context_does_not_authorize_action():
    context = build_context()
    action = build_action()

    assert context.is_remote is True
    assert action.authorization_status == "UNAUTHORIZED"


def test_remote_access_does_not_equal_authorization():
    context = build_context()
    action = build_action()

    assert context.session.state == "CONNECTED"
    assert context.machine.is_available is True
    assert action.authorization_status == "UNAUTHORIZED"


def test_unauthorized_remote_action_cannot_execute():
    action = build_action()

    result = action.execute()

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_is_explicit():
    action = build_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_authorized_action_can_be_distinguished_from_remote_access():
    context = build_context()
    action = build_action()

    action.authorize()

    assert context.is_remote is True
    assert action.authorization_status == "AUTHORIZED"


def test_denied_remote_action_remains_denied():
    action = build_action()

    action.deny()

    assert action.authorization_status == "DENIED"


def test_denied_action_cannot_execute():
    action = build_action()

    action.deny()

    result = action.execute()

    assert result is False
    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_context_does_not_expose_authorization_method():
    context = build_context()

    assert not hasattr(
        context,
        "authorize",
    )

    assert not hasattr(
        context,
        "approve",
    )


def test_remote_context_does_not_execute_action():
    context = build_context()

    assert not hasattr(
        context,
        "execute",
    )

    assert not hasattr(
        context,
        "execute_remediation",
    )