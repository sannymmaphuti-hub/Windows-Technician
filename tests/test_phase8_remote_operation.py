# ==========================================
# Windows Technician V1.0
# PHASE 8.2 REMOTE OPERATION MODEL
# ==========================================

import pytest

from engine.remote_operation import RemoteOperation


def build_operation():
    return RemoteOperation(
        operation_id="remote-op-001",
        machine_id="machine-001",
        session_id="session-001",
    )


def test_operation_requires_operation_id():
    with pytest.raises(ValueError):
        RemoteOperation(
            None,
            "machine-001",
            "session-001",
        )


def test_operation_requires_machine_id():
    with pytest.raises(ValueError):
        RemoteOperation(
            "remote-op-001",
            None,
            "session-001",
        )


def test_operation_requires_session_id():
    with pytest.raises(ValueError):
        RemoteOperation(
            "remote-op-001",
            "machine-001",
            None,
        )


def test_operation_type_is_diagnostic():
    operation = build_operation()

    assert operation.operation_type == "DIAGNOSTIC"


def test_invalid_operation_type_is_rejected():
    with pytest.raises(ValueError):
        RemoteOperation(
            "remote-op-001",
            "machine-001",
            "session-001",
            operation_type="REMediation",
        )


def test_initial_state_is_pending():
    operation = build_operation()

    assert operation.state == "PENDING"


def test_operation_can_start():
    operation = build_operation()

    operation.start()

    assert operation.state == "RUNNING"


def test_operation_can_complete():
    operation = build_operation()

    operation.start()
    operation.complete()

    assert operation.state == "COMPLETED"


def test_operation_can_fail():
    operation = build_operation()

    operation.start()
    operation.fail("remote connection lost")

    assert operation.state == "FAILED"
    assert operation.failure == "remote connection lost"


def test_failure_reason_is_required():
    operation = build_operation()

    with pytest.raises(ValueError):
        operation.fail(None)


def test_completed_operation_cannot_be_started_again():
    operation = build_operation()

    operation.start()
    operation.complete()

    with pytest.raises(ValueError):
        operation.start()


def test_completed_operation_cannot_fail():
    operation = build_operation()

    operation.start()
    operation.complete()

    with pytest.raises(ValueError):
        operation.fail("late failure")


def test_remote_operation_contains_identity():
    operation = build_operation()

    assert operation.operation_id == "remote-op-001"
    assert operation.machine_id == "machine-001"
    assert operation.session_id == "session-001"


def test_remote_operation_has_no_remediation_authorization():
    operation = build_operation()

    assert not hasattr(
        operation,
        "authorize",
    )
    assert not hasattr(
        operation,
        "execute_remediation",
    )


def test_remote_operation_does_not_execute_any_action():
    operation = build_operation()

    assert not hasattr(
        operation,
        "execute",
    )
