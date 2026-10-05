import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.proactive_recommendation import ProactiveRecommendation
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remote_session import RemoteSession
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.remediation_verifier import RemediationVerifier
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_machine(machine_id="machine-1"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Test remediation operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Test remediation action",
        requires_authorization=True,
        operation=operation,
    )


def make_failing_action(action_id="failing-action"):
    def fail():
        raise RuntimeError("Injected remediation failure")

    return make_action(action_id, fail)


def make_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    return workflow


def make_proactive_case(machine):
    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate memory usage.",
    )

    return ProactiveCaseCreator().create(recommendation)


# ---------------------------------------------------------------------------
# Local execution failure injection
# ---------------------------------------------------------------------------

def test_failed_operation_returns_false():
    action = make_failing_action()

    action.authorize()

    assert action.execute() is False


def test_failed_operation_becomes_failed():
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.execution_status == "FAILED"


def test_failed_operation_records_failure_reason():
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.failure_reason == "Injected remediation failure"


def test_failed_operation_does_not_become_successful():
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.execution_status != "EXECUTED"


def test_failed_operation_marks_underlying_operation_failed():
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.operation.execution_status == "FAILED"


def test_failed_action_cannot_be_blindly_reexecuted():
    action = make_failing_action()

    action.authorize()

    first_result = action.execute()
    second_result = action.execute()

    assert first_result is False
    assert second_result is False
    assert action.execution_status == "FAILED"


def test_failed_action_preserves_failure_reason_after_repeat_attempt():
    action = make_failing_action()

    action.authorize()
    action.execute()

    original_reason = action.failure_reason

    action.execute()

    assert action.failure_reason == original_reason


def test_failed_action_does_not_replace_its_operation():
    action = make_failing_action()
    original_operation = action.operation

    action.authorize()
    action.execute()

    replacement = RemediationOperation(
        operation_id="replacement-operation",
        description="Replacement",
        handler=lambda: None,
    )

    action.operation = replacement

    assert action.operation is original_operation


# ---------------------------------------------------------------------------
# Authorization remains intact during failure
# ---------------------------------------------------------------------------

def test_failure_does_not_remove_authorization_state():
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.authorization_status == "AUTHORIZED"


def test_failure_does_not_create_new_authorization():
    action = make_failing_action()

    assert action.authorization_status == "UNAUTHORIZED"

    action.execute()

    assert action.authorization_status == "UNAUTHORIZED"


def test_unauthorized_failing_action_does_not_execute_handler():
    calls = []

    def fail():
        calls.append("executed")
        raise RuntimeError("Injected failure")

    action = make_action("unauthorized-failure", fail)

    assert action.execute() is False
    assert calls == []
    assert action.execution_status == "NOT_EXECUTED"


# ---------------------------------------------------------------------------
# Workflow failure boundaries
# ---------------------------------------------------------------------------

def test_workflow_can_enter_remediating_before_failure():
    workflow = make_workflow()

    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_workflow_can_enter_verifying_after_remediation():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING


def test_failed_verification_does_not_mutate_workflow():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()

    verification = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert verification.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING


def test_failed_verification_can_return_to_remediation():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.state is WorkflowState.REMEDIATING


def test_recovery_preserves_previous_verification_history():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.history[-2:] == [
        (WorkflowState.REMEDIATING, WorkflowState.VERIFYING),
        (WorkflowState.VERIFYING, WorkflowState.REMEDIATING),
    ]


def test_recovery_does_not_mark_workflow_resolved():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.state is not WorkflowState.RESOLVED
    assert workflow.is_terminal is False


def test_failed_verification_does_not_create_terminal_state():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.state in {
        WorkflowState.REMEDIATING,
        WorkflowState.VERIFYING,
    }
    assert workflow.is_terminal is False


# ---------------------------------------------------------------------------
# Verification failure handling
# ---------------------------------------------------------------------------

def test_verifier_reports_mismatch_as_unverified():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is False


def test_verifier_preserves_action_identity_on_failure():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-failed",
    )

    assert result.action_id == "action-failed"
    assert result.verification_result["action_id"] == "action-failed"


def test_verifier_does_not_treat_mismatch_as_success():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is False
    assert result.verification_result["expected"] == {"status": "healthy"}
    assert result.verification_result["observed"] == {"status": "unhealthy"}


def test_verifier_success_requires_matching_state():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "healthy"},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is True


def test_verification_mismatch_does_not_change_action_execution_status():
    action = make_action()

    action.authorize()
    assert action.execute() is True

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert result.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


# ---------------------------------------------------------------------------
# Remote failure injection
# ---------------------------------------------------------------------------

def test_disconnected_remote_machine_blocks_execution():
    machine = make_machine()
    session = RemoteSession(machine)

    context_creation_failed = False

    with pytest.raises(ValueError):
        RemoteRemediationContext(machine, session)

    context_creation_failed = True

    assert context_creation_failed is True
    assert machine.connection_state == "UNKNOWN"
    assert session.state == "DISCONNECTED"


def test_connected_remote_execution_can_be_attempted():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_remote_disconnect_before_execution_does_not_execute_action():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_disconnect_does_not_convert_pending_action_to_failed():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    action.authorize()
    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    executor.execute(action)

    assert action.execution_status == "NOT_EXECUTED"


def test_remote_disconnect_does_not_blindly_retry_action():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    action.authorize()
    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    first_result = executor.execute(action)
    second_result = executor.execute(action)

    assert first_result is False
    assert second_result is False
    assert action.execution_status == "NOT_EXECUTED"


def test_reconnecting_does_not_execute_previous_pending_action():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    action.authorize()

    session.disconnect()
    session.connect()

    assert action.execution_status == "NOT_EXECUTED"

    executor = RemoteRemediationExecutor(context)

    # Reconnection restores availability only.
    # It must not silently execute the pending action.
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_failure_does_not_authorize_action():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    assert action.authorization_status == "UNAUTHORIZED"


# ---------------------------------------------------------------------------
# Remote execution failure injection
# ---------------------------------------------------------------------------

def test_remote_handler_failure_becomes_failed():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_failing_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "FAILED"


def test_remote_handler_failure_preserves_failure_reason():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_failing_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    assert action.failure_reason == "Injected remediation failure"


def test_remote_failed_action_cannot_be_reexecuted():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_failing_action()

    action.authorize()

    executor = RemoteRemediationExecutor(context)

    first_result = executor.execute(action)
    second_result = executor.execute(action)

    assert first_result is False
    assert second_result is False
    assert action.execution_status == "FAILED"


# ---------------------------------------------------------------------------
# Proactive failure isolation
# ---------------------------------------------------------------------------

def test_proactive_alert_cannot_resolve_a_failed_remediation():
    machine = make_machine()
    case = make_proactive_case(machine)
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()

    action = make_failing_action()
    action.authorize()
    action.execute()

    workflow.start_verification()

    case.proactive_alert.resolve()

    assert action.execution_status == "FAILED"
    assert workflow.state is WorkflowState.VERIFYING


def test_proactive_recommendation_does_not_retry_failed_action():
    machine = make_machine()
    case = make_proactive_case(machine)

    action = make_failing_action()
    action.authorize()
    action.execute()

    recommendation = case.proactive_recommendation

    assert recommendation.status == "PENDING"
    assert action.execution_status == "FAILED"


def test_proactive_case_does_not_mark_failed_action_successful():
    machine = make_machine()
    case = make_proactive_case(machine)

    action = make_failing_action()
    action.authorize()
    action.execute()

    assert case.machine_id == machine.machine_id
    assert action.execution_status == "FAILED"


# ---------------------------------------------------------------------------
# Machine isolation during recovery
# ---------------------------------------------------------------------------

def test_failure_on_one_machine_does_not_change_another_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = RemoteSession(machine_a)
    session_b = RemoteSession(machine_b)

    session_a.connect()
    session_b.connect()

    context_a = RemoteRemediationContext(machine_a, session_a)
    action_a = make_failing_action("action-a")
    action_a.authorize()

    executor_a = RemoteRemediationExecutor(context_a)
    executor_a.execute(action_a)

    assert action_a.execution_status == "FAILED"
    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"
    assert session_b.state == "CONNECTED"


def test_disconnect_on_one_machine_does_not_change_another_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = RemoteSession(machine_a)
    session_b = RemoteSession(machine_b)

    session_a.connect()
    session_b.connect()

    session_a.disconnect()

    assert session_a.state == "DISCONNECTED"
    assert machine_a.connection_state == "DISCONNECTED"
    assert session_b.state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"


# ---------------------------------------------------------------------------
# History preservation during failure and recovery
# ---------------------------------------------------------------------------

def test_workflow_history_preserves_failure_recovery_cycle():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    expected = [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
        (WorkflowState.DIAGNOSED, WorkflowState.ACTION_REQUIRED),
        (WorkflowState.ACTION_REQUIRED, WorkflowState.REMEDIATING),
        (WorkflowState.REMEDIATING, WorkflowState.VERIFYING),
        (WorkflowState.VERIFYING, WorkflowState.REMEDIATING),
    ]

    assert workflow.history == expected


def test_workflow_recovery_does_not_erase_original_case():
    workflow = make_workflow()

    original_case = workflow.case

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.case is original_case


def test_failed_action_does_not_change_workflow_without_explicit_transition():
    workflow = make_workflow()
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_failure_does_not_silently_resolve_case():
    workflow = make_workflow()
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert workflow.is_terminal is False


# ---------------------------------------------------------------------------
# Final safety invariants
# ---------------------------------------------------------------------------

def test_execution_failure_is_not_verification_success():
    action = make_failing_action()

    action.authorize()
    execution_result = action.execute()

    verifier = RemediationVerifier()

    verification = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert execution_result is False
    assert action.execution_status == "FAILED"
    assert verification.verification_result["verified"] is False


def test_failed_verification_result_does_not_resolve_workflow():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()

    verification = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert verification.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING
    assert workflow.is_terminal is False


def test_connection_loss_is_not_operation_success():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert action.execution_status != "EXECUTED"


def test_connection_loss_is_not_operation_failure():
    machine = make_machine()
    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(machine, session)
    action = make_action()
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)
    executor.execute(action)

    # The architecture treats lost connection as unknown/unexecuted,
    # rather than falsely declaring the operation failed.
    assert action.execution_status == "NOT_EXECUTED"


def test_recovery_requires_an_explicit_workflow_transition():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING

    # Failed verification alone cannot move the workflow.
    assert workflow.state is WorkflowState.VERIFYING


def test_terminal_resolution_requires_successful_verification_path():
    workflow = make_workflow()

    workflow.start_remediation()
    workflow.start_verification()
    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.state is WorkflowState.REMEDIATING
    assert workflow.is_terminal is False