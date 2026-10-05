# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION VERIFICATION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remote_remediation_executor import (
    RemoteRemediationExecutor,
)
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_context(machine):
    session = RemoteSession(machine)
    session.connect()

    return RemoteRemediationContext(
        machine,
        session,
    )


def build_operation(handler=None):
    if handler is None:
        def handler():
            return None

    return RemediationOperation(
        operation_id="memory_review",
        description="Review memory pressure",
        handler=handler,
    )


def build_action(operation=None):
    return RemediationAction(
        action_id="remote-action-001",
        description="Review high memory usage",
        category="MEMORY",
        severity="HIGH",
        operation=operation,
    )


def execute_remote_action(context, action):
    executor = RemoteRemediationExecutor(context)

    action.authorize()

    return executor.execute(action)


def test_remote_execution_can_be_followed_by_existing_verification():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["verified"] is True


def test_remote_execution_success_does_not_equal_verification_success():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.action_id == action.action_id
    assert result.verification_result["verified"] is False


def test_failed_verification_does_not_change_execution_to_failed():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_successful_remote_verification_preserves_action_identity():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id=action.action_id,
    )

    assert result.action_id == "remote-action-001"
    assert result.verification_result["action_id"] == "remote-action-001"


def test_remote_verification_preserves_machine_identity():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id=action.action_id,
    )

    assert context.machine_id == "machine-001"
    assert context.hostname == "REMOTE-PC"
    assert context.session_id is not None
    assert result.action_id == action.action_id


def test_verification_requires_matching_expected_and_observed_state():
    verifier = RemediationVerifier()

    success = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id="action-001",
    )

    failure = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id="action-001",
    )

    assert success.verification_result["verified"] is True
    assert failure.verification_result["verified"] is False


def test_disconnected_remote_machine_does_not_execute_before_verification():
    machine = build_machine()
    context = build_context(machine)
    context.session.disconnect()

    operation = build_operation()
    action = build_action(operation)

    executor = RemoteRemediationExecutor(context)

    action.authorize()

    result = executor.execute(action)

    assert result is False
    assert action.execution_status == "NOT_EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"


def test_remote_verification_is_not_automatic():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    assert action.execution_status == "EXECUTED"


def test_remote_verification_does_not_execute_action_again():
    calls = []

    def handler():
        calls.append(True)

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is True
    assert calls == [True]


def test_failed_remote_verification_does_not_trigger_automatic_retry():
    calls = []

    def handler():
        calls.append(True)

    machine = build_machine()
    context = build_context(machine)
    operation = build_operation(handler)
    action = build_action(operation)

    assert execute_remote_action(context, action) is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert calls == [True]
    assert action.execution_status == "EXECUTED"


def test_remote_verification_reuses_existing_verifier():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="RESOLVED",
        action_id="remote-action-001",
    )

    assert result.action_id == "remote-action-001"
    assert result.verification_result["verified"] is True


def test_remote_context_does_not_create_a_second_verifier():
    machine = build_machine()
    context = build_context(machine)

    assert not hasattr(context, "verify")
    assert not hasattr(context, "verify_remediation")


def test_remote_verification_failure_remains_distinct_from_execution_failure():
    machine = build_machine()
    context = build_context(machine)
    operation = build_operation()
    action = build_action(operation)

    assert execute_remote_action(context, action) is True
    assert action.execution_status == "EXECUTED"

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="RESOLVED",
        observed="STILL_PRESENT",
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"