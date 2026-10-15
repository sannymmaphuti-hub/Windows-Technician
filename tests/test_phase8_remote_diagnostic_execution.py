# ==========================================
# Windows Technician V1.0
# PHASE 8.3 REMOTE DIAGNOSTIC EXECUTION
# ==========================================

import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.observation import Observation
from engine.remote_session import RemoteSession
from engine.remote_technician_operations import (
    RemoteTechnicianOperations,
)
from engine.remote_diagnostic_execution import (
    RemoteDiagnosticExecution,
)


def build_operations():
    machine = ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    session = RemoteSession(machine)
    session.connect()

    return RemoteTechnicianOperations(
        machine,
        session,
    )


def build_observations():
    return [
        Observation(
            source="remote",
            subject="network",
            attribute="adapter_status",
            value="disconnected",
        ),
    ]


def test_execution_requires_operations():
    with pytest.raises(ValueError):
        RemoteDiagnosticExecution(None)


def test_execution_starts_operation():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    execution.execute(
        build_observations()
    )

    assert execution.operation is not None
    assert execution.operation.state == "COMPLETED"


def test_execution_creates_diagnostic_operation():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    execution.execute(
        build_observations()
    )

    assert execution.operation.operation_type == "DIAGNOSTIC"


def test_execution_preserves_machine_identity():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    execution.execute(
        build_observations()
    )

    assert (
        execution.operation.machine_id
        == operations.machine_id
    )


def test_execution_preserves_session_identity():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    execution.execute(
        build_observations()
    )

    assert (
        execution.operation.session_id
        == operations.session_id
    )


def test_execution_returns_canonical_case():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    result = execution.execute(
        build_observations()
    )

    assert isinstance(
        result,
        DiagnosticCase,
    )


def test_execution_stores_result():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    result = execution.execute(
        build_observations()
    )

    assert execution.result is result


def test_execution_cannot_run_twice():
    operations = build_operations()
    execution = RemoteDiagnosticExecution(
        operations
    )

    execution.execute(
        build_observations()
    )

    with pytest.raises(ValueError):
        execution.execute(
            build_observations()
        )


def test_unavailable_machine_is_rejected():
    operations = build_operations()
    operations.machine.connection_state = "DISCONNECTED"

    execution = RemoteDiagnosticExecution(
        operations
    )

    with pytest.raises(ValueError):
        execution.execute(
            build_observations()
        )


def test_pipeline_failure_marks_operation_failed():
    operations = build_operations()

    class FailingPipeline:
        def diagnose(self, remote_input):
            raise RuntimeError(
                "diagnostic pipeline failed"
            )

    operations.diagnostic_pipeline = FailingPipeline()

    execution = RemoteDiagnosticExecution(
        operations
    )

    with pytest.raises(RuntimeError):
        execution.execute(
            build_observations()
        )

    assert execution.operation.state == "FAILED"
    assert (
        execution.failure
        == "diagnostic pipeline failed"
    )


def test_pipeline_failure_does_not_create_remediation():
    operations = build_operations()

    class FailingPipeline:
        def diagnose(self, remote_input):
            raise RuntimeError(
                "diagnostic pipeline failed"
            )

    operations.diagnostic_pipeline = FailingPipeline()

    execution = RemoteDiagnosticExecution(
        operations
    )

    with pytest.raises(RuntimeError):
        execution.execute(
            build_observations()
        )

    assert not hasattr(
        execution,
        "authorize_remediation",
    )

    assert not hasattr(
        execution,
        "execute_remediation",
    )
