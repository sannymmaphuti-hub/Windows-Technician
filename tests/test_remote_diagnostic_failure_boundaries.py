# ==========================================
# Windows Technician v0.8
# REMOTE DIAGNOSTIC FAILURE & BOUNDARY TESTS
# ==========================================

import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.observation import Observation


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


def build_valid_input():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteDiagnosticContext(
        machine,
        session,
    )

    observations = [
        Observation(
            source="remote",
            subject="network",
            attribute="adapter_status",
            value="disconnected",
        ),
    ]

    return RemoteDiagnosticInput(
        context,
        observations,
    )


def test_disconnected_machine_cannot_create_diagnostic_context():
    machine = build_machine()
    session = RemoteSession(machine)

    assert machine.is_available is False

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine,
            session,
        )


def test_session_must_belong_to_machine():
    machine_one = build_machine()

    machine_two = ManagedMachine(
        machine_id="machine-002",
        hostname="OTHER-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = build_connected_session(machine_one)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine_two,
            session,
        )


def test_remote_input_requires_valid_context():
    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            None,
            [],
        )


def test_remote_input_requires_observations_argument():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteDiagnosticContext(
        machine,
        session,
    )

    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context,
            None,
        )


def test_pipeline_rejects_non_remote_input():
    pipeline = RemoteDiagnosticPipeline()

    with pytest.raises(ValueError):
        pipeline.diagnose(None)


def test_pipeline_rejects_wrong_input_type():
    pipeline = RemoteDiagnosticPipeline()

    with pytest.raises(ValueError):
        pipeline.diagnose(
            object()
        )


def test_failed_session_does_not_report_machine_as_available():
    machine = build_machine()
    session = RemoteSession(machine)

    session.state = "FAILED"
    machine.connection_state = "FAILED"

    assert machine.is_available is False


def test_disconnected_session_does_not_allow_diagnosis_context():
    machine = build_machine()
    session = RemoteSession(machine)

    assert session.state == "DISCONNECTED"
    assert machine.is_available is False

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine,
            session,
        )


def test_empty_remote_observations_are_safe():
    machine = build_machine()
    session = build_connected_session(machine)

    context = RemoteDiagnosticContext(
        machine,
        session,
    )

    remote_input = RemoteDiagnosticInput(
        context,
        [],
    )

    result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert result["observations"] == []
    assert result["signals"] == []
    assert result["findings"] == []


def test_remote_input_observations_are_not_mutated():
    remote_input = build_valid_input()

    original = remote_input.observations

    RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert remote_input.observations == original


def test_remote_diagnostic_does_not_change_session_state():
    remote_input = build_valid_input()

    session = remote_input.context.session

    assert session.state == "CONNECTED"

    RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert session.state == "CONNECTED"


def test_remote_diagnostic_does_not_change_machine_availability():
    remote_input = build_valid_input()

    machine = remote_input.context.machine

    assert machine.is_available is True

    RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    assert machine.is_available is True