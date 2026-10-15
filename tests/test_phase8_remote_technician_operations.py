# ==========================================
# Windows Technician V1.0
# PHASE 8.1 REMOTE TECHNICIAN OPERATIONS
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_technician_operations import (
    RemoteTechnicianOperations,
)
from engine.observation import Observation


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def build_observations():
    return [
        Observation(
            source="remote",
            subject="network",
            attribute="adapter_status",
            value="disconnected",
        ),
    ]


def build_operations():
    machine = build_machine()
    session = build_session(machine)

    return (
        RemoteTechnicianOperations(
            machine,
            session,
        ),
        machine,
        session,
    )


def test_requires_managed_machine():
    machine = object()
    session = object()

    with pytest.raises(ValueError):
        RemoteTechnicianOperations(
            machine,
            session,
        )


def test_requires_remote_session():
    machine = build_machine()

    with pytest.raises(ValueError):
        RemoteTechnicianOperations(
            machine,
            object(),
        )


def test_session_must_belong_to_machine():
    machine = build_machine()
    other_machine = build_machine()
    session = build_session(other_machine)

    with pytest.raises(ValueError):
        RemoteTechnicianOperations(
            machine,
            session,
        )


def test_disconnected_machine_cannot_start_operations():
    machine = build_machine()
    session = build_session(machine)
    session.disconnect()

    with pytest.raises(ValueError):
        RemoteTechnicianOperations(
            machine,
            session,
        )


def test_operation_is_remote():
    operations, _, _ = build_operations()

    assert operations.is_remote is True


def test_remote_diagnosis_returns_canonical_case():
    operations, _, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert isinstance(
        case,
        DiagnosticCase,
    )


def test_remote_case_preserves_machine_identity():
    operations, machine, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname


def test_remote_case_preserves_session_identity():
    operations, _, session = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert case.session_id == session.session_id


def test_remote_case_origin_is_remote():
    operations, _, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert case.origin == "REMOTE"


def test_remote_case_uses_canonical_case_type():
    operations, _, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert type(case) is DiagnosticCase


def test_remote_diagnosis_preserves_observations():
    operations, _, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert len(case.observations) == 1
    assert case.observations[0].subject == "network"


def test_remote_diagnosis_does_not_authorize_remediation():
    operations, _, _ = build_operations()

    case = operations.diagnose(
        build_observations()
    )

    assert not hasattr(
        case,
        "authorize_remediation",
    )


def test_remote_diagnosis_does_not_execute_remediation():
    operations, _, _ = build_operations()

    operations.diagnose(
        build_observations()
    )

    assert operations.case is not None
    assert operations.result is not None
