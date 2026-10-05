import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession
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


def create_action(
    action_id="action-001",
    operation=None,
    requires_authorization=True,
):
    return RemediationAction(
        action_id=action_id,
        description="Authorization abuse test action.",
        requires_authorization=requires_authorization,
        operation=operation,
    )


def create_remote_environment():
    machine = create_machine()

    session = RemoteSession(machine)
    session.connect()

    context = RemoteRemediationContext(
        machine=machine,
        session=session,
    )

    return machine, session, context


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


def progress_to_action_required(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()


# ============================================================
# INITIAL AUTHORIZATION STATE
# ============================================================


def test_action_starts_unauthorized():
    action = create_action()

    assert action.authorization_status == "UNAUTHORIZED"


def test_action_starts_unexecuted():
    action = create_action()

    assert action.execution_status == "NOT_EXECUTED"


def test_action_requires_explicit_authorization_before_execution():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    assert action.execute() is False
    assert executions == []
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# AUTHORIZATION MUST BE ACTION-SPECIFIC
# ============================================================


def test_authorizing_one_action_does_not_authorize_another():
    action_a = create_action(
        action_id="action-a",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="action-b",
        operation=lambda: None,
    )

    action_a.authorize()

    assert action_a.authorization_status == "AUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"

    assert action_b.execute() is False
    assert action_b.execution_status == "NOT_EXECUTED"


def test_authorization_is_not_shared_between_actions():
    action_a = create_action(action_id="action-a")
    action_b = create_action(action_id="action-b")

    action_a.authorize()

    assert action_a.authorization_status == "AUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"


def test_denial_of_one_action_does_not_change_another():
    action_a = create_action(action_id="action-a")
    action_b = create_action(action_id="action-b")

    action_a.deny()

    assert action_a.authorization_status == "DENIED"
    assert action_b.authorization_status == "UNAUTHORIZED"


# ============================================================
# AUTHORIZE / DENY ABUSE
# ============================================================


def test_deny_then_authorize_does_not_bypass_denial():
    action = create_action(operation=lambda: None)

    action.deny()
    action.authorize()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_authorize_then_deny_does_not_execute():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.authorize()
    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_multiple_denials_remain_denied():
    action = create_action()

    action.deny()
    action.deny()
    action.deny()

    assert action.authorization_status == "DENIED"


def test_repeated_authorization_is_idempotent():
    action = create_action()

    action.authorize()
    action.authorize()
    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_denied_action_cannot_become_authorized():
    action = create_action()

    action.deny()

    for _ in range(3):
        action.authorize()

    assert action.authorization_status == "DENIED"


# ============================================================
# EXECUTION ORDER ABUSE
# ============================================================


def test_execute_before_authorize_cannot_be_followed_by_successful_execution_without_authorization():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    assert action.execute() is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    assert action.execute() is True
    assert executions == [True]
    assert action.execution_status == "EXECUTED"


def test_failed_unauthorized_execution_does_not_consume_action():
    action = create_action(operation=lambda: None)

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    assert action.execute() is True
    assert action.execution_status == "EXECUTED"


def test_denied_execution_does_not_consume_action_as_executed():
    action = create_action(operation=lambda: None)

    action.deny()

    assert action.execute() is False
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# NON-AUTHORIZED ACTION TYPES
# ============================================================


def test_action_without_required_authorization_can_execute_when_operation_exists():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(
        operation=operation,
        requires_authorization=False,
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execute() is True
    assert executions == [True]
    assert action.execution_status == "EXECUTED"


def test_authorization_status_does_not_override_requires_authorization_contract():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(
        operation=operation,
        requires_authorization=False,
    )

    action.deny()

    assert action.execute() is True
    assert executions == [True]
    assert action.execution_status == "EXECUTED"


# ============================================================
# OPERATION MUTATION AFTER AUTHORIZATION
# ============================================================


def test_authorized_action_can_execute_its_bound_operation():
    executions = []

    def operation():
        executions.append("original")

    action = create_action(operation=operation)

    action.authorize()

    assert action.execute() is True
    assert executions == ["original"]


def test_operation_can_be_bound_before_authorization():
    executions = []

    def operation():
        executions.append(True)

    action = create_action()

    action.operation = operation

    assert action.execution_status == "NOT_EXECUTED"
    assert action.authorization_status == "UNAUTHORIZED"

    action.authorize()

    assert action.execute() is True
    assert executions == [True]


def test_operation_can_be_replaced_before_execution():
    executions = []

    def first_operation():
        executions.append("first")

    def second_operation():
        executions.append("second")

    action = create_action(operation=first_operation)

    action.operation = second_operation
    action.authorize()

    assert action.execute() is True
    assert executions == ["second"]


def test_operation_cannot_be_replaced_after_execution():
    executions = []

    def first_operation():
        executions.append("first")

    def second_operation():
        executions.append("second")

    action = create_action(operation=first_operation)
    action.authorize()

    assert action.execute() is True

    action.operation = second_operation

    assert action.execute() is False
    assert executions == ["first"]


def test_operation_cannot_be_replaced_after_failure():
    executions = []

    def failing_operation():
        executions.append("failure")
        raise RuntimeError("forced failure")

    def replacement_operation():
        executions.append("replacement")

    action = create_action(operation=failing_operation)
    action.authorize()

    assert action.execute() is False

    action.operation = replacement_operation

    assert action.execute() is False
    assert executions == ["failure"]
    assert action.execution_status == "FAILED"


# ============================================================
# EXECUTION FAILURE / AUTHORIZATION ABUSE
# ============================================================


def test_failed_action_remains_failed_after_reauthorization_attempt():
    def operation():
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)

    action.authorize()

    assert action.execute() is False
    assert action.execution_status == "FAILED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "FAILED"

    assert action.execute() is False


def test_failed_action_cannot_be_reset_by_denial():
    def operation():
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)

    action.authorize()
    action.execute()

    action.deny()

    assert action.execution_status == "FAILED"


def test_failed_action_does_not_silently_retry():
    executions = []

    def operation():
        executions.append(True)
        raise RuntimeError("forced failure")

    action = create_action(operation=operation)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False

    assert executions == [True]


# ============================================================
# COMPLETED ACTION AUTHORIZATION ABUSE
# ============================================================


def test_executed_action_remains_executed_after_deny_attempt():
    action = create_action(operation=lambda: None)

    action.authorize()
    assert action.execute() is True

    action.deny()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"


def test_executed_action_remains_executed_after_authorize_attempt():
    action = create_action(operation=lambda: None)

    action.authorize()
    assert action.execute() is True

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"


def test_executed_action_cannot_execute_again_after_authorization_changes():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.authorize()
    assert action.execute() is True

    action.deny()
    action.authorize()

    assert action.execute() is False
    assert executions == [True]


# ============================================================
# REMOTE AUTHORIZATION BOUNDARY
# ============================================================


def test_remote_session_does_not_authorize_action():
    _, _, context = create_remote_environment()

    action = create_action(operation=lambda: None)

    assert context.machine.connection_state == "CONNECTED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_remote_executor_does_not_authorize_action():
    _, _, context = create_remote_environment()

    action = create_action(operation=lambda: None)

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_executor_requires_action_authorization():
    _, _, context = create_remote_environment()

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executions == []


def test_remote_authorization_does_not_authorize_other_action():
    _, _, context = create_remote_environment()

    action_a = create_action(
        action_id="action-a",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="action-b",
        operation=lambda: None,
    )

    action_a.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action_a) is True
    assert executor.execute(action_b) is False

    assert action_a.execution_status == "EXECUTED"
    assert action_b.authorization_status == "UNAUTHORIZED"
    assert action_b.execution_status == "NOT_EXECUTED"


def test_remote_disconnect_does_not_revoke_or_grant_authorization():
    machine, session, context = create_remote_environment()

    action = create_action(operation=lambda: None)
    action.authorize()

    assert action.authorization_status == "AUTHORIZED"

    session.disconnect()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    session.connect()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_remote_connection_alone_never_grants_execution():
    _, _, context = create_remote_environment()

    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executions == []


# ============================================================
# REMOTE MACHINE ISOLATION
# ============================================================


def test_authorization_on_machine_a_does_not_authorize_action_for_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = RemoteSession(machine_a)
    session_a.connect()

    context_a = RemoteRemediationContext(
        machine=machine_a,
        session=session_a,
    )

    action_a = create_action(
        action_id="machine-a-action",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="machine-b-action",
        operation=lambda: None,
    )

    action_a.authorize()

    executor_a = RemoteRemediationExecutor(context_a)

    assert executor_a.execute(action_a) is True
    assert executor_a.execute(action_b) is False

    assert action_b.authorization_status == "UNAUTHORIZED"
    assert action_b.execution_status == "NOT_EXECUTED"
    assert machine_b.connection_state == "UNKNOWN"


def test_session_for_machine_a_cannot_create_context_for_machine_b():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = RemoteSession(machine_a)
    session_a.connect()

    with pytest.raises(ValueError):
        RemoteRemediationContext(
            machine=machine_b,
            session=session_a,
        )


# ============================================================
# WORKFLOW DOES NOT GRANT AUTHORIZATION
# ============================================================


def test_case_access_does_not_authorize_action():
    case = create_case()

    workflow = TechnicianWorkflow(case)
    action = create_action()

    assert workflow.case is case
    assert action.authorization_status == "UNAUTHORIZED"


def test_workflow_progression_does_not_authorize_action():
    workflow = TechnicianWorkflow(create_case())
    action = create_action()

    progress_to_action_required(workflow)

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"


def test_action_required_state_does_not_execute_action():
    executions = []

    def operation():
        executions.append(True)

    workflow = TechnicianWorkflow(create_case())
    action = create_action(operation=operation)

    progress_to_action_required(workflow)

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


def test_remediating_state_does_not_authorize_action():
    workflow = TechnicianWorkflow(create_case())
    action = create_action()

    progress_to_action_required(workflow)
    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING
    assert action.authorization_status == "UNAUTHORIZED"


def test_verifying_state_does_not_authorize_action():
    workflow = TechnicianWorkflow(create_case())
    action = create_action()

    progress_to_action_required(workflow)
    workflow.start_remediation()
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING
    assert action.authorization_status == "UNAUTHORIZED"


# ============================================================
# PROACTIVE AUTHORIZATION BOUNDARY
# ============================================================


def test_proactive_alert_does_not_authorize_action():
    _, alert, _, _ = create_proactive_chain()

    action = create_action()

    assert alert.status == "ACTIVE"
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_recommendation_does_not_authorize_action():
    _, _, recommendation, _ = create_proactive_chain()

    action = create_action()

    assert recommendation.status == "PENDING"
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_case_does_not_authorize_action():
    _, _, _, case = create_proactive_chain()

    workflow = TechnicianWorkflow(case)
    action = create_action()

    assert workflow.state is WorkflowState.OPEN
    assert action.authorization_status == "UNAUTHORIZED"


def test_proactive_chain_does_not_execute_action():
    executions = []

    def operation():
        executions.append(True)

    _, _, recommendation, case = create_proactive_chain()

    action = create_action(operation=operation)

    assert recommendation.status == "PENDING"
    assert case.proactive_recommendation is recommendation
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []


# ============================================================
# ACTION IDENTITY
# ============================================================


def test_actions_keep_distinct_identity():
    action_a = create_action(action_id="action-a")
    action_b = create_action(action_id="action-b")

    assert action_a.action_id != action_b.action_id


def test_authorizing_action_does_not_modify_other_action_identity():
    action_a = create_action(action_id="action-a")
    action_b = create_action(action_id="action-b")

    action_a.authorize()

    assert action_a.action_id == "action-a"
    assert action_b.action_id == "action-b"


def test_execution_state_is_action_specific():
    action_a = create_action(
        action_id="action-a",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="action-b",
        operation=lambda: None,
    )

    action_a.authorize()
    action_a.execute()

    assert action_a.execution_status == "EXECUTED"
    assert action_b.execution_status == "NOT_EXECUTED"


# ============================================================
# AUTHORIZATION DOES NOT BYPASS WORKFLOW
# ============================================================


def test_authorized_action_does_not_skip_workflow():
    workflow = TechnicianWorkflow(create_case())

    action = create_action(operation=lambda: None)
    action.authorize()

    assert action.execute() is True
    assert workflow.state is WorkflowState.OPEN


def test_authorized_action_does_not_resolve_workflow():
    workflow = TechnicianWorkflow(create_case())

    action = create_action(operation=lambda: None)
    action.authorize()
    action.execute()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


def test_workflow_resolution_does_not_authorize_new_action():
    workflow = TechnicianWorkflow(create_case())

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    action = create_action()

    assert workflow.state is WorkflowState.RESOLVED
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# FINAL ABUSE INVARIANTS
# ============================================================


def test_authorization_abuse_cannot_turn_denial_into_execution():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.deny()
    action.authorize()

    assert action.authorization_status == "DENIED"
    assert action.execute() is False
    assert executions == []
    assert action.execution_status == "NOT_EXECUTED"


def test_authorization_abuse_cannot_repeat_completed_operation():
    executions = []

    def operation():
        executions.append(True)

    action = create_action(operation=operation)

    action.authorize()
    assert action.execute() is True

    action.authorize()
    assert action.execute() is False

    assert executions == [True]


def test_authorization_abuse_cannot_repeat_failed_operation():
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


def test_authorization_abuse_cannot_cross_action_boundary():
    executions = []

    def operation():
        executions.append(True)

    authorized_action = create_action(
        action_id="authorized-action",
        operation=operation,
    )

    unauthorized_action = create_action(
        action_id="unauthorized-action",
        operation=operation,
    )

    authorized_action.authorize()

    assert authorized_action.execute() is True
    assert unauthorized_action.execute() is False

    assert executions == [True]
    assert unauthorized_action.authorization_status == "UNAUTHORIZED"
    assert unauthorized_action.execution_status == "NOT_EXECUTED"


def test_authorization_abuse_cannot_cross_machine_boundary():
    machine_a = create_machine("machine-a", "PC-A")
    machine_b = create_machine("machine-b", "PC-B")

    session_a = RemoteSession(machine_a)
    session_a.connect()

    context_a = RemoteRemediationContext(
        machine=machine_a,
        session=session_a,
    )

    action_a = create_action(
        action_id="machine-a-action",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="machine-b-action",
        operation=lambda: None,
    )

    action_a.authorize()

    executor_a = RemoteRemediationExecutor(context_a)

    assert executor_a.execute(action_a) is True
    assert executor_a.execute(action_b) is False

    assert action_b.authorization_status == "UNAUTHORIZED"
    assert action_b.execution_status == "NOT_EXECUTED"
    assert machine_b.connection_state == "UNKNOWN"


def test_authorization_abuse_cannot_cross_workflow_boundary():
    workflow_a = TechnicianWorkflow(
        create_case("machine-a", "PC-A")
    )

    workflow_b = TechnicianWorkflow(
        create_case("machine-b", "PC-B")
    )

    action_a = create_action(
        action_id="workflow-a-action",
        operation=lambda: None,
    )

    action_b = create_action(
        action_id="workflow-b-action",
        operation=lambda: None,
    )

    action_a.authorize()

    assert action_a.authorization_status == "AUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"

    assert workflow_a.state is WorkflowState.OPEN
    assert workflow_b.state is WorkflowState.OPEN


def test_final_authorization_safety_invariant():
    action = create_action(operation=lambda: None)

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is True

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"

    assert action.execute() is False
    assert action.execution_status == "EXECUTED"