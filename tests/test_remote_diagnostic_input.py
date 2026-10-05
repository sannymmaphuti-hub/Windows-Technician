import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput


def create_context():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="TECH-PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    return RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )


def test_remote_diagnostic_input_requires_context():
    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context=None,
            observations=[],
        )


def test_remote_diagnostic_input_requires_remote_context():
    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context="not-a-context",
            observations=[],
        )


def test_remote_diagnostic_input_requires_observations():
    context = create_context()

    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context=context,
            observations=None,
        )


def test_remote_diagnostic_input_stores_context():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert diagnostic_input.context is context


def test_remote_diagnostic_input_stores_observations():
    context = create_context()
    observations = ["observation-1", "observation-2"]

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=observations,
    )

    assert diagnostic_input.observations == observations


def test_remote_diagnostic_input_exposes_machine_id():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert diagnostic_input.machine_id == "machine-001"


def test_remote_diagnostic_input_exposes_session_id():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert diagnostic_input.session_id == context.session_id


def test_remote_diagnostic_input_is_remote():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert diagnostic_input.is_remote is True


def test_remote_diagnostic_input_preserves_observation_order():
    context = create_context()
    observations = [
        "cpu-observation",
        "memory-observation",
        "network-observation",
    ]

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=observations,
    )

    assert diagnostic_input.observations == observations


def test_remote_diagnostic_input_returns_copy_of_observations():
    context = create_context()
    observations = ["observation-1"]

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=observations,
    )

    returned = diagnostic_input.observations
    returned.append("observation-2")

    assert diagnostic_input.observations == ["observation-1"]


def test_remote_diagnostic_input_does_not_create_diagnostic_case():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert not hasattr(diagnostic_input, "case")
    assert not hasattr(diagnostic_input, "diagnostic_case")
    assert not hasattr(diagnostic_input, "create_case")


def test_remote_diagnostic_input_does_not_create_workflow():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert not hasattr(diagnostic_input, "workflow")
    assert not hasattr(diagnostic_input, "technician_workflow")


def test_remote_diagnostic_input_does_not_execute_remediation():
    context = create_context()

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert not hasattr(diagnostic_input, "execute")
    assert not hasattr(diagnostic_input, "remediate")
    assert not hasattr(diagnostic_input, "remediation")