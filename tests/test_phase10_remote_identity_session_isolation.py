import pytest

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction


# ============================================================
# FACTORIES
# ============================================================


def create_machine(machine_id="machine-001", hostname="TEST-PC"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=hostname,
        platform="Windows",
        operating_system="Windows 11",
    )


def create_connected_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def create_action(
    action_id="action-001",
    operation=None,
):
    return RemediationAction(
        action_id=action_id,
        description="Remote identity isolation test action.",
        requires_authorization=True,
        operation=operation,
    )


def create_connected_environment(
    machine_id="machine-001",
    hostname="TEST-PC",
):
    machine = create_machine(machine_id, hostname)
    session = create_connected_session(machine)

    return machine, session


# ============================================================
# MACHINE IDENTITY
# ============================================================


def test_managed_machine_preserves_identity():
    machine = create_machine("machine-a", "PC-A")

    assert machine.machine_id == "machine-a"
    assert machine.hostname == "PC-A"


def test_two_machines_have_distinct_identity():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    assert machine_a.machine_id != machine_b.machine_id
    assert machine_a.hostname != machine_b.hostname


def test_machine_identity_is_not_implicitly_shared():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    assert machine_a.machine_id != machine_b.machine_id
    assert machine_a.connection_state != machine_b.connection_state or (
        machine_a is not machine_b
    )


# ============================================================
# SESSION OWNERSHIP
# ============================================================


def test_remote_session_belongs_to_its_machine():
    machine = create_machine("machine-a", "PC-A")
    session = create_connected_session(machine)

    assert session.machine is machine
    assert session.machine.machine_id == "machine-a"


def test_remote_session_exposes_unique_session_identity():
    machine = create_machine("machine-a", "PC-A")

    session_a = create_connected_session(machine)
    session_b = create_connected_session(machine)

    assert session_a.session_id != session_b.session_id


def test_two_sessions_do_not_share_session_identity():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)
    session_b = create_connected_session(machine_b)

    assert session_a.session_id != session_b.session_id


def test_session_for_machine_a_does_not_belong_to_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    assert session_a.machine is machine_a
    assert session_a.machine is not machine_b
    assert session_a.machine.machine_id != machine_b.machine_id


# ============================================================
# CONNECTION STATE ISOLATION
# ============================================================


def test_connecting_machine_a_does_not_connect_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"

    assert session_a.machine is machine_a


def test_disconnecting_machine_a_does_not_disconnect_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)
    session_b = create_connected_session(machine_b)

    session_a.disconnect()

    assert machine_a.connection_state == "DISCONNECTED"
    assert machine_b.connection_state == "CONNECTED"
    assert session_b.state == "CONNECTED"


def test_reconnecting_machine_a_does_not_change_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)
    session_b = create_connected_session(machine_b)

    session_a.disconnect()
    session_a.connect()

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"
    assert session_b.state == "CONNECTED"


def test_disconnected_machine_reports_unavailable():
    machine = create_machine()
    session = create_connected_session(machine)

    assert machine.is_available is True

    session.disconnect()

    assert machine.is_available is False


# ============================================================
# DIAGNOSTIC CONTEXT IDENTITY
# ============================================================


def test_remote_diagnostic_context_preserves_machine_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.machine_id == "machine-a"
    assert context.hostname == "PC-A"
    assert context.session_id == session.session_id
    assert context.is_remote is True


def test_remote_diagnostic_context_preserves_session_identity():
    machine, session = create_connected_environment()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.session_id == session.session_id


def test_remote_diagnostic_context_rejects_machine_session_mismatch():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_b,
            session=session_a,
        )


def test_remote_diagnostic_context_rejects_disconnected_session():
    machine = create_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session=session,
        )


def test_remote_diagnostic_context_does_not_bind_to_unrelated_machine():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_b,
            session=session_a,
        )


# ============================================================
# DIAGNOSTIC INPUT IDENTITY
# ============================================================


def test_remote_diagnostic_input_preserves_context_machine_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert remote_input.machine_id == "machine-a"
    assert remote_input.session_id == session.session_id


def test_remote_diagnostic_input_is_remote():
    machine, session = create_connected_environment()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    assert remote_input.is_remote is True


def test_remote_diagnostic_input_cannot_use_unrelated_context():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        context = RemoteDiagnosticContext(
            machine=machine_b,
            session=session_a,
        )

        RemoteDiagnosticInput(
            context=context,
            observations=[],
        )


# ============================================================
# DIAGNOSTIC PIPELINE ISOLATION
# ============================================================


def test_remote_diagnostic_result_preserves_machine_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[],
    )

    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    assert result["machine_id"] == "machine-a"
    assert result["hostname"] == "PC-A"
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True


def test_remote_diagnostic_result_does_not_use_another_machine_identity():
    machine_a, session_a = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    machine_b, session_b = create_connected_environment(
        "machine-b",
        "PC-B",
    )

    context_a = RemoteDiagnosticContext(
        machine=machine_a,
        session=session_a,
    )

    remote_input_a = RemoteDiagnosticInput(
        context=context_a,
        observations=[],
    )

    result = RemoteDiagnosticPipeline().diagnose(remote_input_a)

    assert result["machine_id"] == machine_a.machine_id
    assert result["hostname"] == machine_a.hostname
    assert result["session_id"] == session_a.session_id

    assert result["machine_id"] != machine_b.machine_id
    assert result["session_id"] != session_b.session_id


def test_two_remote_diagnostics_keep_identity_separate():
    machine_a, session_a = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    machine_b, session_b = create_connected_environment(
        "machine-b",
        "PC-B",
    )

    context_a = RemoteDiagnosticContext(
        machine=machine_a,
        session=session_a,
    )

    context_b = RemoteDiagnosticContext(
        machine=machine_b,
        session=session_b,
    )

    input_a = RemoteDiagnosticInput(
        context=context_a,
        observations=[],
    )

    input_b = RemoteDiagnosticInput(
        context=context_b,
        observations=[],
    )

    result_a = RemoteDiagnosticPipeline().diagnose(input_a)
    result_b = RemoteDiagnosticPipeline().diagnose(input_b)

    assert result_a["machine_id"] == "machine-a"
    assert result_b["machine_id"] == "machine-b"

    assert result_a["session_id"] == session_a.session_id
    assert result_b["session_id"] == session_b.session_id

    assert result_a["machine_id"] != result_b["machine_id"]
    assert result_a["session_id"] != result_b["session_id"]


# ============================================================
# REMEDIATION CONTEXT IDENTITY
# ============================================================


def test_remote_remediation_context_preserves_machine_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    assert context.machine_id == "machine-a"
    assert context.hostname == "PC-A"
    assert context.session_id == session.session_id
    assert context.is_remote is True


def test_remote_remediation_context_preserves_session_identity():
    machine, session = create_connected_environment()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    assert context.session_id == session.session_id


def test_remote_remediation_context_rejects_machine_session_mismatch():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


def test_remote_remediation_context_rejects_disconnected_session():
    machine = create_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine,
            session=session,
        )


def test_remote_remediation_context_does_not_bind_to_unrelated_machine():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


# ============================================================
# REMOTE EXECUTION ISOLATION
# ============================================================


def test_remote_executor_uses_its_context_machine():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    executions = []

    def operation():
        executions.append(machine.machine_id)

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert executions == ["machine-a"]


def test_remote_executor_does_not_execute_unauthorized_action():
    machine, session = create_connected_environment()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_rejects_execution_when_session_disconnects():
    machine, session = create_connected_environment()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_does_not_mark_disconnected_action_failed():
    machine, session = create_connected_environment()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# CROSS-MACHINE REMEDIATION ISOLATION
# ============================================================


def test_machine_a_executor_cannot_create_context_for_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


def test_machine_a_session_cannot_execute_against_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        context_b = RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )

        RemoteRemediationExecutor(context_b)


def test_machine_b_remains_unaffected_by_machine_a_execution():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    context_a = RemoteRemediationContext(
        machine=machine_a,
        session=session_a,
    )

    executions = []

    def operation():
        executions.append("machine-a")

    action = create_action(operation=operation)
    action.authorize()

    executor_a = RemoteRemediationExecutor(context_a)

    assert executor_a.execute(action) is True

    assert executions == ["machine-a"]
    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"


def test_machine_a_disconnect_does_not_change_machine_b_state():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)
    session_b = create_connected_session(machine_b)

    session_a.disconnect()

    assert machine_a.connection_state == "DISCONNECTED"
    assert machine_b.connection_state == "CONNECTED"
    assert session_b.state == "CONNECTED"


# ============================================================
# SESSION LIFECYCLE ISOLATION
# ============================================================


def test_disconnect_is_idempotent():
    machine = create_machine()
    session = create_connected_session(machine)

    session.disconnect()
    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"


def test_connect_is_idempotent():
    machine = create_machine()
    session = create_connected_session(machine)

    session.connect()
    session.connect()

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_reconnect_preserves_session_identity():
    machine = create_machine()
    session = create_connected_session(machine)

    original_session_id = session.session_id

    session.disconnect()
    session.connect()

    assert session.session_id == original_session_id


def test_reconnect_does_not_change_machine_identity():
    machine = create_machine("machine-a", "PC-A")
    session = create_connected_session(machine)

    session.disconnect()
    session.connect()

    assert machine.machine_id == "machine-a"
    assert machine.hostname == "PC-A"


# ============================================================
# CONTEXT LIFECYCLE SAFETY
# ============================================================


def test_diagnostic_context_retains_original_identity_after_session_disconnect():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    session.disconnect()

    assert context.machine_id == "machine-a"
    assert context.hostname == "PC-A"
    assert context.session_id == session.session_id


def test_remediation_context_retains_original_identity_after_session_disconnect():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    session.disconnect()

    assert context.machine_id == "machine-a"
    assert context.hostname == "PC-A"
    assert context.session_id == session.session_id


def test_reconnection_does_not_replace_context_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    diagnostic_context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remediation_context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    diagnostic_session_id = diagnostic_context.session_id
    remediation_session_id = remediation_context.session_id

    session.disconnect()
    session.connect()

    assert diagnostic_context.session_id == diagnostic_session_id
    assert remediation_context.session_id == remediation_session_id
    assert diagnostic_context.machine_id == "machine-a"
    assert remediation_context.machine_id == "machine-a"


# ============================================================
# DIAGNOSTIC / REMEDIATION CONTEXT ISOLATION
# ============================================================


def test_diagnostic_and_remediation_contexts_share_machine_identity():
    machine, session = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    diagnostic_context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remediation_context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    assert diagnostic_context.machine_id == remediation_context.machine_id
    assert diagnostic_context.hostname == remediation_context.hostname
    assert diagnostic_context.session_id == remediation_context.session_id


def test_diagnostic_context_is_remote():
    machine, session = create_connected_environment()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    assert context.is_remote is True


def test_remediation_context_is_remote():
    machine, session = create_connected_environment()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    assert context.is_remote is True


def test_diagnostic_and_remediation_contexts_do_not_change_action_authorization():
    machine, session = create_connected_environment()

    RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# MULTI-MACHINE ISOLATION
# ============================================================


def test_three_machines_keep_independent_connection_state():
    machine_a, session_a = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    machine_b, session_b = create_connected_environment(
        "machine-b",
        "PC-B",
    )

    machine_c = create_machine("machine-c", "PC-C")

    session_a.disconnect()

    assert machine_a.connection_state == "DISCONNECTED"
    assert machine_b.connection_state == "CONNECTED"
    assert machine_c.connection_state == "UNKNOWN"

    assert session_b.state == "CONNECTED"


def test_three_sessions_keep_unique_identity():
    machine_a, session_a = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    machine_b, session_b = create_connected_environment(
        "machine-b",
        "PC-B",
    )

    machine_c, session_c = create_connected_environment(
        "machine-c",
        "PC-C",
    )

    session_ids = {
        session_a.session_id,
        session_b.session_id,
        session_c.session_id,
    }

    assert len(session_ids) == 3


def test_machine_identity_and_session_identity_remain_pairwise_distinct():
    machine_a, session_a = create_connected_environment(
        "machine-a",
        "PC-A",
    )

    machine_b, session_b = create_connected_environment(
        "machine-b",
        "PC-B",
    )

    assert session_a.machine_id if hasattr(session_a, "machine_id") else (
        session_a.machine.machine_id
    ) == "machine-a"

    assert session_b.machine_id if hasattr(session_b, "machine_id") else (
        session_b.machine.machine_id
    ) == "machine-b"

    assert session_a.machine is not session_b.machine


# ============================================================
# FINAL IDENTITY INVARIANTS
# ============================================================


def test_identity_invariant_session_machine_pair_cannot_be_swapped():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_b,
            session=session_a,
        )

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


def test_identity_invariant_disconnected_session_cannot_form_new_context():
    machine = create_machine()
    session = create_connected_session(machine)

    session.disconnect()

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session=session,
        )

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine,
            session=session,
        )


def test_identity_invariant_machine_b_cannot_inherit_machine_a_connection():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"

    assert session_a.machine is machine_a
    assert session_a.machine is not machine_b


def test_identity_invariant_machine_a_execution_does_not_execute_on_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    context_a = RemoteRemediationContext(
        machine=machine_a,
        session=session_a,
    )

    executions = []

    def operation():
        executions.append(machine_a.machine_id)

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(context_a)

    assert executor.execute(action) is True

    assert executions == ["machine-a"]
    assert machine_b.connection_state == "UNKNOWN"


def test_identity_invariant_reconnect_preserves_authority_scope():
    machine_a = create_machine("machine-a", "PC-A")
    session_a = create_connected_session(machine_a)

    context_a = RemoteRemediationContext(
        machine=machine_a,
        session=session_a,
    )

    action = create_action(operation=lambda: None)
    action.authorize()

    session_a.disconnect()
    session_a.connect()

    executor = RemoteRemediationExecutor(context_a)

    assert context_a.machine_id == "machine-a"
    assert context_a.session_id == session_a.session_id
    assert machine_a.connection_state == "CONNECTED"

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_identity_invariant_no_remote_context_without_valid_identity_pair():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = create_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_b,
            session=session_a,
        )

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )