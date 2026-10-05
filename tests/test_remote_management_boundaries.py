from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession


def create_machine():
    return ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )


def test_remote_session_exposes_managed_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    assert session.machine is machine


def test_remote_session_exposes_machine_identity():
    machine = create_machine()
    session = RemoteSession(machine)

    assert session.machine.machine_id == "machine-1"
    assert session.machine.hostname == "PC-01"


def test_remote_session_does_not_create_diagnostic_case():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "case")
    assert not hasattr(session, "diagnostic_case")
    assert not hasattr(session, "create_case")


def test_remote_session_does_not_create_workflow():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "workflow")
    assert not hasattr(session, "technician_workflow")
    assert not hasattr(session, "create_workflow")


def test_remote_session_does_not_expose_diagnosis_operation():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "diagnose")
    assert not hasattr(session, "run_diagnostics")


def test_remote_session_does_not_expose_remediation_operation():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "remediate")
    assert not hasattr(session, "execute_remediation")


def test_remote_session_does_not_bypass_authorization():
    session = RemoteSession(create_machine())

    assert not hasattr(session, "authorize")
    assert not hasattr(session, "approve")
    assert not hasattr(session, "execute")


def test_machine_and_session_have_separate_identity():
    machine = create_machine()
    session = RemoteSession(machine)

    assert machine.machine_id != session.session_id


def test_multiple_sessions_can_reference_same_machine():
    machine = create_machine()

    session_one = RemoteSession(machine)
    session_two = RemoteSession(machine)

    assert session_one.machine is machine
    assert session_two.machine is machine
    assert session_one.session_id != session_two.session_id


def test_session_does_not_replace_machine_identity():
    machine = create_machine()
    session = RemoteSession(machine)

    session.connect()

    assert machine.machine_id == "machine-1"
    assert session.machine is machine


def test_remote_management_preserves_existing_workflow_boundary():
    machine = create_machine()
    session = RemoteSession(machine)

    assert not hasattr(machine, "workflow")
    assert not hasattr(session, "workflow")


def test_remote_management_preserves_existing_case_boundary():
    machine = create_machine()
    session = RemoteSession(machine)

    assert not hasattr(machine, "case")
    assert not hasattr(session, "case")