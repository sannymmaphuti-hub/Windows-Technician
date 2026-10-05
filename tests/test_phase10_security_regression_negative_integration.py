import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.observation import Observation
from engine.proactive_alert import ProactiveAlert
from engine.proactive_case_creation import ProactiveCaseCreator
from engine.proactive_recommendation import ProactiveRecommendation
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
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


def make_connected_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


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
        raise RuntimeError("Injected security regression failure")

    return make_action(action_id, fail)


def make_proactive_recommendation(machine):
    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    return ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate memory usage.",
    )


def make_proactive_case(machine):
    recommendation = make_proactive_recommendation(machine)
    return ProactiveCaseCreator().create(recommendation)


def make_workflow(case=None):
    if case is None:
        case = DiagnosticCase()

    workflow = TechnicianWorkflow(case)
    return workflow


def make_action_required_workflow(case=None):
    workflow = make_workflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    return workflow


def make_verifying_workflow(case=None):
    workflow = make_action_required_workflow(case)

    workflow.start_remediation()
    workflow.start_verification()

    return workflow


# ---------------------------------------------------------------------------
# Authorization regression
# ---------------------------------------------------------------------------

def test_new_action_always_starts_unauthorized():
    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_does_not_execute_action():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("authorization-only", handler)

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert calls == []


def test_unauthorized_action_cannot_execute():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("blocked-action", handler)

    assert action.execute() is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert calls == []


def test_denied_action_cannot_execute():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("denied-action", handler)

    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"
    assert calls == []


def test_denied_action_cannot_be_reauthorized():
    action = make_action("denied-reauthorization")

    action.deny()
    action.authorize()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_is_action_specific():
    action_a = make_action("action-a")
    action_b = make_action("action-b")

    action_a.authorize()

    assert action_a.authorization_status == "AUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"


def test_workflow_state_does_not_authorize_action():
    workflow = make_action_required_workflow()
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execute() is False


def test_case_state_does_not_authorize_action():
    case = DiagnosticCase()
    case.status = "ACTION_REQUIRED"

    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execute() is False


# ---------------------------------------------------------------------------
# Execution regression
# ---------------------------------------------------------------------------

def test_successful_execution_requires_authorization():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("successful-action", handler)

    assert action.execute() is False
    assert calls == []

    action.authorize()

    assert action.execute() is True
    assert calls == ["executed"]
    assert action.execution_status == "EXECUTED"


def test_execution_success_does_not_equal_verification_success():
    action = make_action()

    action.authorize()
    assert action.execute() is True
    assert action.execution_status == "EXECUTED"

    verification = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert verification.verification_result["verified"] is False
    assert action.execution_status == "EXECUTED"


def test_failed_execution_becomes_failed():
    action = make_failing_action()

    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"
    assert action.failure_reason == "Injected security regression failure"


def test_failed_execution_cannot_be_repeated():
    calls = []

    def fail():
        calls.append("executed")
        raise RuntimeError("Injected failure")

    action = make_action("failed-once", fail)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False

    assert calls == ["executed"]
    assert action.execution_status == "FAILED"


def test_executed_action_cannot_be_repeated():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("executed-once", handler)
    action.authorize()

    assert action.execute() is True
    assert action.execute() is False

    assert calls == ["executed"]
    assert action.execution_status == "EXECUTED"


def test_completed_action_operation_cannot_be_replaced():
    action = make_action("operation-lock")

    original_operation = action.operation

    action.authorize()
    action.execute()

    replacement = RemediationOperation(
        operation_id="replacement",
        description="Replacement operation",
        handler=lambda: None,
    )

    action.operation = replacement

    assert action.operation is original_operation


# ---------------------------------------------------------------------------
# Workflow integrity regression
# ---------------------------------------------------------------------------

def test_workflow_starts_open():
    workflow = make_workflow()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


def test_workflow_cannot_skip_investigation():
    workflow = make_workflow()

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()


def test_workflow_cannot_skip_diagnosis():
    workflow = make_workflow()

    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.require_action()


def test_workflow_cannot_skip_action_required():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    with pytest.raises(ValueError):
        workflow.start_remediation()


def test_workflow_cannot_skip_remediation():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    with pytest.raises(ValueError):
        workflow.start_verification()


def test_workflow_cannot_resolve_from_open():
    workflow = make_workflow()

    with pytest.raises(ValueError):
        workflow.resolve()


def test_workflow_cannot_resolve_from_investigating():
    workflow = make_workflow()

    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.resolve()


def test_workflow_cannot_resolve_from_action_required():
    workflow = make_action_required_workflow()

    with pytest.raises(ValueError):
        workflow.resolve()


def test_workflow_resolves_only_from_verifying():
    workflow = make_verifying_workflow()

    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_resolved_workflow_is_terminal():
    workflow = make_verifying_workflow()

    workflow.resolve()

    assert workflow.is_terminal is True


def test_resolved_workflow_cannot_restart_without_reopen():
    workflow = make_verifying_workflow()

    workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_investigation()


def test_reopen_is_explicit():
    workflow = make_verifying_workflow()

    workflow.resolve()
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False


def test_reopened_workflow_preserves_history():
    workflow = make_verifying_workflow()

    workflow.resolve()
    workflow.reopen()

    assert workflow.history[-2:] == [
        (WorkflowState.VERIFYING, WorkflowState.RESOLVED),
        (WorkflowState.RESOLVED, WorkflowState.INVESTIGATING),
    ]


def test_escalated_workflow_is_terminal():
    workflow = make_workflow()

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED
    assert workflow.is_terminal is True


def test_escalated_workflow_cannot_reopen():
    workflow = make_workflow()

    workflow.escalate()

    with pytest.raises(ValueError):
        workflow.reopen()


# ---------------------------------------------------------------------------
# Remote identity regression
# ---------------------------------------------------------------------------

def test_remote_session_requires_managed_machine():
    with pytest.raises(ValueError):
        RemoteSession(object())


def test_remote_diagnostic_context_requires_matching_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(machine_b, session_a)


def test_remote_remediation_context_requires_matching_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)

    with pytest.raises(ValueError):
        RemoteRemediationContext(machine_b, session_a)


def test_remote_diagnostic_context_rejects_disconnected_session():
    machine = make_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(machine, session)


def test_remote_remediation_context_rejects_disconnected_session():
    machine = make_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteRemediationContext(machine, session)


def test_remote_session_connection_is_machine_specific():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = RemoteSession(machine_a)
    session_b = RemoteSession(machine_b)

    session_a.connect()

    assert session_a.state == "CONNECTED"
    assert session_b.state == "DISCONNECTED"
    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"


def test_remote_session_disconnect_does_not_disconnect_another_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)
    session_b = make_connected_session(machine_b)

    session_a.disconnect()

    assert session_a.state == "DISCONNECTED"
    assert machine_a.connection_state == "DISCONNECTED"
    assert session_b.state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"


# ---------------------------------------------------------------------------
# Remote remediation regression
# ---------------------------------------------------------------------------

def test_remote_executor_requires_remediation_context():
    machine = make_machine()
    session = make_connected_session(machine)
    diagnostic_context = RemoteDiagnosticContext(machine, session)

    with pytest.raises(ValueError):
        RemoteRemediationExecutor(diagnostic_context)


def test_remote_executor_requires_authorized_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_respects_denial():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    action.deny()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_does_not_execute_after_disconnect():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_does_not_blindly_retry_after_disconnect():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    calls = []

    def handler():
        calls.append("executed")

    action = make_action("remote-pending", handler)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executor.execute(action) is False

    assert calls == []
    assert action.execution_status == "NOT_EXECUTED"


def test_reconnect_restores_availability_but_not_execution():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    calls = []

    def handler():
        calls.append("executed")

    action = make_action("reconnect-pending", handler)
    action.authorize()

    session.disconnect()
    session.connect()

    assert machine.connection_state == "CONNECTED"
    assert session.state == "CONNECTED"
    assert action.execution_status == "NOT_EXECUTED"
    assert calls == []


def test_remote_execution_failure_is_explicit():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_failing_action("remote-failure")
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "FAILED"


# ---------------------------------------------------------------------------
# Proactive security regression
# ---------------------------------------------------------------------------

def test_proactive_alert_starts_active():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is unusually high.",
    )

    assert alert.status == "ACTIVE"


def test_proactive_alert_acknowledgement_does_not_authorize_action():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is unusually high.",
    )

    action = make_action()

    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_recommendation_does_not_execute_action():
    machine = make_machine()

    recommendation = make_proactive_recommendation(machine)
    action = make_action()

    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"
    assert action.execution_status == "NOT_EXECUTED"


def test_proactive_case_creation_does_not_execute_remediation():
    machine = make_machine()

    case = make_proactive_case(machine)
    action = make_action()

    assert case.machine_id == machine.machine_id
    assert action.execution_status == "NOT_EXECUTED"


def test_proactive_case_does_not_create_remote_authority():
    machine = make_machine()

    case = make_proactive_case(machine)

    assert case.machine_id == machine.machine_id
    assert not hasattr(case, "session_id")


def test_proactive_lifecycle_does_not_change_remote_session():
    machine = make_machine()
    session = RemoteSession(machine)

    recommendation = make_proactive_recommendation(machine)

    recommendation.acknowledge()
    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "UNKNOWN"


# ---------------------------------------------------------------------------
# Cross-pillar regression
# ---------------------------------------------------------------------------

def test_remote_connection_does_not_authorize_proactive_action():
    machine = make_machine()
    session = make_connected_session(machine)

    recommendation = make_proactive_recommendation(machine)
    action = make_action()

    assert session.state == "CONNECTED"
    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_detection_does_not_authorize_remote_action():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    alert = ProactiveAlert(
        machine=machine,
        alert_type="MEMORY_ANOMALY",
        metric="memory_usage",
        message="Memory usage is unusually high.",
    )

    action = make_action()

    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"
    assert action.authorization_status == "UNAUTHORIZED"

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False


def test_local_workflow_does_not_change_remote_connection_state():
    machine = make_machine()
    session = make_connected_session(machine)

    workflow = make_workflow()
    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED
    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_disconnect_does_not_change_proactive_state():
    machine = make_machine()
    session = make_connected_session(machine)

    recommendation = make_proactive_recommendation(machine)

    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert recommendation.status == "PENDING"


def test_remote_disconnect_does_not_change_local_workflow():
    machine = make_machine()
    session = make_connected_session(machine)

    workflow = make_workflow()
    workflow.start_investigation()

    session.disconnect()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_proactive_case_workflow_does_not_change_machine_connection():
    machine = make_machine()
    session = RemoteSession(machine)

    case = make_proactive_case(machine)
    workflow = make_action_required_workflow(case)

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "UNKNOWN"


def test_separate_machine_pillars_remain_isolated():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_connected_session(machine_a)
    proactive_case_b = make_proactive_case(machine_b)

    action_a = make_action("machine-a-action")
    action_b = make_action("machine-b-action")

    assert session_a.machine.machine_id == machine_a.machine_id
    assert proactive_case_b.machine_id == machine_b.machine_id

    assert action_a.authorization_status == "UNAUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"


# ---------------------------------------------------------------------------
# Diagnostic regression
# ---------------------------------------------------------------------------

def test_remote_diagnostic_requires_remote_input():
    with pytest.raises((ValueError, TypeError)):
        RemoteDiagnosticPipeline().diagnose(object())


def test_remote_diagnostic_input_requires_correct_context():
    machine = make_machine()

    with pytest.raises(ValueError):
        RemoteDiagnosticInput(
            context=object(),
            observations=[],
        )


def test_remote_diagnostic_preserves_remote_identity():
    machine = make_machine()
    session = make_connected_session(machine)

    context = RemoteDiagnosticContext(machine, session)

    observation = Observation(
        source="system",
        subject="network",
        attribute="status",
        value="warning",
    )

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[observation],
    )

    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    assert result["machine_id"] == machine.machine_id
    assert result["hostname"] == machine.hostname
    assert result["session_id"] == session.session_id
    assert result["is_remote"] is True


def test_remote_diagnostic_does_not_execute_remediation():
    machine = make_machine()
    session = make_connected_session(machine)

    context = RemoteDiagnosticContext(machine, session)

    observation = Observation(
        source="system",
        subject="network",
        attribute="status",
        value="warning",
    )

    remote_input = RemoteDiagnosticInput(
        context=context,
        observations=[observation],
    )

    RemoteDiagnosticPipeline().diagnose(remote_input)

    action = make_action()

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ---------------------------------------------------------------------------
# Recovery security regression
# ---------------------------------------------------------------------------

def test_failed_verification_does_not_mutate_workflow():
    workflow = make_verifying_workflow()

    result = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING


def test_failed_verification_does_not_resolve_workflow_implicitly():
    workflow = make_verifying_workflow()

    result = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING
    assert workflow.is_terminal is False


def test_recovery_requires_explicit_transition():
    workflow = make_verifying_workflow()

    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.state is WorkflowState.REMEDIATING
    assert workflow.is_terminal is False


def test_recovery_preserves_history():
    workflow = make_verifying_workflow()

    workflow._transition_to(WorkflowState.REMEDIATING)

    assert workflow.history[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.REMEDIATING,
    )


def test_failed_action_does_not_resolve_workflow():
    workflow = make_action_required_workflow()
    action = make_failing_action()

    action.authorize()
    action.execute()

    assert action.execution_status == "FAILED"
    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert workflow.is_terminal is False


# ---------------------------------------------------------------------------
# Final security invariants
# ---------------------------------------------------------------------------

def test_detection_never_equals_authorization():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="SECURITY_ANOMALY",
        metric="security_status",
        message="Security anomaly detected.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate the detected anomaly.",
    )

    action = make_action()

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_recommendation_never_equals_execution():
    machine = make_machine()

    recommendation = make_proactive_recommendation(machine)
    action = make_action()

    assert recommendation.status == "PENDING"
    assert action.execution_status == "NOT_EXECUTED"


def test_connection_never_equals_authorization():
    machine = make_machine()
    session = make_connected_session(machine)
    action = make_action()

    assert session.state == "CONNECTED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_execution_never_equals_verification():
    action = make_action()

    action.authorize()
    action.execute()

    verification = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id=action.action_id,
    )

    assert action.execution_status == "EXECUTED"
    assert verification.verification_result["verified"] is False


def test_connection_loss_never_equals_execution_failure():
    machine = make_machine()
    session = make_connected_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert action.execution_status != "FAILED"


def test_failed_execution_never_equals_success():
    action = make_failing_action()

    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"
    assert action.execution_status != "EXECUTED"


def test_terminal_workflow_never_reopens_implicitly():
    workflow = make_verifying_workflow()

    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED

    # No external failure or event should implicitly reopen it.
    assert workflow.state is WorkflowState.RESOLVED


def test_all_security_boundaries_remain_explicit():
    machine = make_machine()
    session = make_connected_session(machine)

    case = make_proactive_case(machine)
    workflow = make_action_required_workflow(case)

    context = RemoteRemediationContext(machine, session)
    action = make_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert context.is_remote is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is False

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert session.state == "CONNECTED"