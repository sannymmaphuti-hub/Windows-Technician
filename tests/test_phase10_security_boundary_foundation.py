import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remediation_action import RemediationAction
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation
from engine.proactive_case_creation import ProactiveCaseCreator


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


def create_case(machine_id="machine-001", hostname="TEST-PC"):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = hostname
    return case


def create_action(operation=None):
    return RemediationAction(
        action_id="action-001",
        description="Security boundary test action.",
        requires_authorization=True,
        operation=operation,
    )


def create_connected_remote_environment():
    machine = create_machine()

    session = RemoteSession(machine)
    session.connect()

    diagnostic_context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    remediation_context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return (
        machine,
        session,
        diagnostic_context,
        remediation_context,
    )


def create_proactive_chain():
    machine = create_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="PERFORMANCE_DEGRADATION",
        metric="cpu_usage",
        message="CPU usage exceeded the established baseline.",
    )

    recommendation = ProactiveRecommendation(
        alert=alert,
        recommendation="Investigate sustained CPU usage.",
    )

    case = ProactiveCaseCreator().create(recommendation)

    return machine, alert, recommendation, case


# ============================================================
# REMEDIATION AUTHORIZATION BOUNDARY
# ============================================================


def test_new_action_starts_unauthorized():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_new_action_starts_unexecuted():
    action = create_action()

    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_cannot_execute():
    action = create_action(operation=lambda: None)

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_unauthorized_action_does_not_invoke_operation():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    assert action.execute() is False
    assert executions == []


def test_authorization_must_be_explicit():
    action = create_action(operation=lambda: None)

    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_authorization_alone_does_not_execute():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_denied_action_remains_unexecuted():
    action = create_action(operation=lambda: None)

    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_denied_action_cannot_execute():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.deny()

    assert action.execute() is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"


def test_deny_does_not_execute_operation():
    action = create_action()

    action.deny()

    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# OPERATION SAFETY
# ============================================================


def test_authorized_action_without_operation_cannot_execute():
    action = create_action()

    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


def test_operation_failure_marks_action_failed():
    def operation():
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"


def test_operation_failure_preserves_failure_reason():
    def operation():
        raise RuntimeError("security test failure")

    action = create_action(operation=operation)
    action.authorize()

    action.execute()

    assert action.failure_reason == "security test failure"


def test_failed_action_does_not_become_executed():
    def operation():
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)
    action.authorize()

    action.execute()

    assert action.execution_status == "FAILED"


def test_executed_action_cannot_be_executed_again():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is True
    assert action.execute() is False

    assert executions == [True]
    assert action.execution_status == "EXECUTED"


def test_failed_action_cannot_be_executed_again():
    executions = []

    def operation():
        executions.append(True)
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False

    assert executions == [True]
    assert action.execution_status == "FAILED"


# ============================================================
# ACTION STATE INTEGRITY
# ============================================================


def test_operation_binding_is_allowed_before_execution():
    action = create_action()

    operation = lambda: None

    action.operation = operation

    assert action.operation is operation


def test_operation_cannot_be_replaced_after_execution():
    first_executions = []
    second_executions = []

    def first_operation():
        first_executions.append(True)

    def second_operation():
        second_executions.append(True)

    action = create_action(operation=first_operation)
    action.authorize()

    assert action.execute() is True

    action.operation = second_operation

    assert action.execute() is False
    assert first_executions == [True]
    assert second_executions == []


def test_operation_cannot_be_replaced_after_failure():
    def failing_operation():
        raise RuntimeError("forced failure")

    replacement_executions = []

    def replacement_operation():
        replacement_executions.append(True)

    action = create_action(operation=failing_operation)
    action.authorize()

    assert action.execute() is False

    action.operation = replacement_operation

    assert action.execute() is False
    assert replacement_executions == []
    assert action.execution_status == "FAILED"


def test_authorization_cannot_override_denial():
    action = create_action()

    action.deny()
    action.authorize()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_cannot_change_completed_action():
    action = create_action(operation=lambda: None)

    action.authorize()
    action.execute()

    action.deny()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"


# ============================================================
# REMOTE IDENTITY BOUNDARY
# ============================================================


def test_remote_session_requires_managed_machine():
    with pytest.raises(ValueError):
        RemoteSession(object())


def test_remote_diagnostic_context_requires_same_machine_identity():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session = RemoteSession(machine_a)
    session.connect()

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine_b,
            session=session,
        )


def test_remote_remediation_context_requires_same_machine_identity():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session = RemoteSession(machine_a)
    session.connect()

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session,
        )


def test_remote_diagnostic_context_rejects_disconnected_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteDiagnosticContext(
            machine=machine,
            session=session,
        )


def test_remote_remediation_context_rejects_disconnected_machine():
    machine = create_machine()
    session = RemoteSession(machine)

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine,
            session=session,
        )


# ============================================================
# REMOTE EXECUTION BOUNDARY
# ============================================================


def test_remote_executor_requires_explicit_context():
    _, _, _, remediation_context = create_connected_remote_environment()

    action = create_action()

    executor = RemoteRemediationExecutor(remediation_context)

    assert executor is not None
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_rejects_unauthorized_action():
    _, _, _, remediation_context = (
        create_connected_remote_environment()
    )

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    executor = RemoteRemediationExecutor(remediation_context)

    assert executor.execute(action) is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_allows_authorized_action_when_connected():
    _, _, _, remediation_context = (
        create_connected_remote_environment()
    )

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)
    action.authorize()

    executor = RemoteRemediationExecutor(remediation_context)

    assert executor.execute(action) is True
    assert executions == [True]
    assert action.execution_status == "EXECUTED"


def test_remote_executor_rejects_action_after_connection_loss():
    machine, session, _, remediation_context = (
        create_connected_remote_environment()
    )

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(remediation_context)

    assert executor.execute(action) is False
    assert action.execution_status == "NOT_EXECUTED"
    assert machine.connection_state == "DISCONNECTED"


def test_remote_connection_loss_does_not_mark_unexecuted_action_failed():
    machine, session, _, remediation_context = (
        create_connected_remote_environment()
    )

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()

    executor = RemoteRemediationExecutor(remediation_context)
    executor.execute(action)

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# WORKFLOW STATE SECURITY
# ============================================================


def test_new_workflow_starts_open():
    workflow = TechnicianWorkflow(create_case())

    assert workflow.state is WorkflowState.OPEN


def test_workflow_cannot_skip_investigation():
    workflow = TechnicianWorkflow(create_case())

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.OPEN


def test_workflow_cannot_skip_diagnosis():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.require_action()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_workflow_cannot_start_remediation_from_open():
    workflow = TechnicianWorkflow(create_case())

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.OPEN


def test_workflow_cannot_start_verification_from_open():
    workflow = TechnicianWorkflow(create_case())

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.OPEN


def test_workflow_cannot_resolve_before_verification():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_resolved_workflow_is_terminal():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_resolved_workflow_cannot_start_investigation_without_reopen():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_investigation()

    assert workflow.state is WorkflowState.RESOLVED


def test_reopen_is_the_explicit_path_from_resolved_state():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False


# ============================================================
# PROACTIVE SECURITY BOUNDARY
# ============================================================


def test_proactive_alert_requires_managed_machine():
    with pytest.raises(ValueError):
        ProactiveAlert(
            machine=object(),
            alert_type="TEST",
            metric="cpu",
            message="Test alert.",
        )


def test_proactive_alert_does_not_authorize_remediation():
    _, alert, _, _ = create_proactive_chain()

    assert alert.status == "ACTIVE"


def test_proactive_recommendation_requires_proactive_alert():
    with pytest.raises(ValueError):
        ProactiveRecommendation(
            alert=object(),
            recommendation="Investigate.",
        )


def test_proactive_recommendation_starts_pending():
    _, _, recommendation, _ = create_proactive_chain()

    assert recommendation.status == "PENDING"


def test_proactive_case_creation_does_not_execute_remediation():
    _, _, recommendation, case = create_proactive_chain()

    action = create_action()

    assert case.proactive_recommendation is recommendation
    assert recommendation.status == "PENDING"
    assert action.execution_status == "NOT_EXECUTED"


def test_proactive_case_starts_open():
    _, _, _, case = create_proactive_chain()

    workflow = TechnicianWorkflow(case)

    assert workflow.state is WorkflowState.OPEN


# ============================================================
# CROSS-PILLAR MACHINE ISOLATION
# ============================================================


def test_cases_can_remain_bound_to_different_machines():
    case_a = create_case("machine-a", "PC-A")
    case_b = create_case("machine-b", "PC-B")

    assert case_a.machine_id == "machine-a"
    assert case_b.machine_id == "machine-b"
    assert case_a.machine_id != case_b.machine_id


def test_remote_machine_identity_is_not_interchangeable():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = RemoteSession(machine_a)
    session_a.connect()

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


def test_proactive_case_preserves_alert_machine_identity():
    machine, alert, recommendation, case = create_proactive_chain()

    assert alert.machine_id == machine.machine_id
    assert recommendation.machine_id == machine.machine_id
    assert case.machine_id == machine.machine_id


# ============================================================
# DIAGNOSTIC SAFETY
# ============================================================


def test_remote_diagnostic_requires_remote_input_contract():
    _, _, _, _ = create_connected_remote_environment()

    pipeline = RemoteDiagnosticPipeline()

    with pytest.raises((ValueError, TypeError, AttributeError)):
        pipeline.diagnose(object())


def test_remote_diagnostic_input_preserves_remote_machine_identity():
    machine, session, diagnostic_context, _ = (
        create_connected_remote_environment()
    )

    remote_input = RemoteDiagnosticInput(
        context=diagnostic_context,
        observations=[],
    )

    assert remote_input.machine_id == machine.machine_id
    assert remote_input.session_id == session.session_id


def test_diagnostic_execution_does_not_authorize_remediation():
    machine, session, diagnostic_context, _ = (
        create_connected_remote_environment()
    )

    remote_input = RemoteDiagnosticInput(
        context=diagnostic_context,
        observations=[],
    )

    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    action = create_action()

    assert result["is_remote"] is True
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# FINAL SECURITY INVARIANTS
# ============================================================


def test_security_invariant_detection_does_not_execute():
    _, _, _, case = create_proactive_chain()

    action = create_action()

    assert case is not None
    assert action.execution_status == "NOT_EXECUTED"


def test_security_invariant_recommendation_does_not_execute():
    _, _, recommendation, _ = create_proactive_chain()

    action = create_action()

    assert recommendation.status == "PENDING"
    assert action.execution_status == "NOT_EXECUTED"


def test_security_invariant_authorization_does_not_execute():
    action = create_action(operation=lambda: None)

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_security_invariant_execution_does_not_resolve_workflow():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    action = create_action(operation=lambda: None)
    action.authorize()

    assert action.execute() is True
    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_security_invariant_connection_loss_does_not_equal_failure():
    machine, session, _, _ = create_connected_remote_environment()

    action = create_action(operation=lambda: None)
    action.authorize()

    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"


def test_security_invariant_terminal_state_cannot_be_bypassed():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.RESOLVED


def test_security_invariant_history_is_preserved_after_reopen():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    history_before_reopen = list(workflow.history)

    workflow.reopen()

    assert workflow.history[:6] == history_before_reopen
    assert workflow.history[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_security_invariant_remote_execution_requires_both_connection_and_authorization():
    machine, session, _, remediation_context = (
        create_connected_remote_environment()
    )

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    executor = RemoteRemediationExecutor(remediation_context)

    # Connected, but unauthorized.
    assert executor.execute(action) is False
    assert executions == []

    # Authorized, but disconnected.
    action.authorize()
    session.disconnect()

    assert executor.execute(action) is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"

    # Reconnected and explicitly authorized.
    session.connect()

    assert executor.execute(action) is True
    assert executions == [True]
    assert action.execution_status == "EXECUTED"
    assert machine.connection_state == "CONNECTED"