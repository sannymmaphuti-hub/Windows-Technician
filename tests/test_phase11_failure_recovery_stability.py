import time

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


def make_machine(machine_id="machine-1"):
    return ManagedMachine(
        machine_id=machine_id,
        hostname=f"HOST-{machine_id}",
        platform="Windows",
        operating_system="Windows 11",
    )


def make_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def make_observation(
    subject="network",
    attribute="status",
    value="warning",
):
    return Observation(
        source="system",
        subject=subject,
        attribute=attribute,
        value=value,
    )


def make_remote_input(machine, session):
    return RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(machine, session),
        observations=[make_observation()],
    )


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Failure recovery operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Failure recovery action",
        requires_authorization=True,
        operation=operation,
    )


def make_failing_action(action_id="failing-action"):
    def handler():
        raise RuntimeError("injected failure")

    return make_action(action_id, handler)


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


def prepare_workflow_for_verification():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    return workflow


def test_failed_remediation_preserves_action_identity():
    action = make_failing_action("failure-identity")
    original_id = action.action_id

    action.authorize()

    assert action.execute() is False
    assert action.action_id == original_id


def test_failed_remediation_preserves_failure_reason():
    action = make_failing_action("failure-reason")

    action.authorize()

    assert action.execute() is False
    assert action.failure_reason == "injected failure"


def test_failed_remediation_does_not_execute_again():
    calls = []

    def handler():
        calls.append("attempt")
        raise RuntimeError("injected failure")

    action = make_action("no-repeat", handler)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False
    assert action.execute() is False

    assert calls == ["attempt"]
    assert action.execution_status == "FAILED"


def test_failed_remediation_preserves_authorization_state():
    action = make_failing_action("authorization-preserved")

    action.authorize()
    action.execute()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "FAILED"


def test_failed_remote_remediation_preserves_machine_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_failing_action("remote-identity")
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False

    assert context.machine_id == machine.machine_id
    assert session.machine.machine_id == machine.machine_id


def test_failed_remote_remediation_preserves_session_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    original_session_id = session.session_id

    action = make_failing_action("remote-session")
    action.authorize()

    assert RemoteRemediationExecutor(context).execute(action) is False

    assert session.session_id == original_session_id
    assert context.session_id == original_session_id


def test_failed_remote_remediation_does_not_disconnect_machine():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_failing_action("remote-connection")
    action.authorize()

    assert RemoteRemediationExecutor(context).execute(action) is False

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_failed_remote_remediation_does_not_repeat_after_failure():
    calls = []

    def handler():
        calls.append("attempt")
        raise RuntimeError("remote injected failure")

    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action("remote-no-repeat", handler)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    for _ in range(25):
        assert executor.execute(action) is False

    assert calls == ["attempt"]
    assert action.execution_status == "FAILED"
    assert action.failure_reason == "remote injected failure"


def test_connection_loss_does_not_mutate_action_to_failed():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action("connection-loss")
    action.authorize()

    session.disconnect()

    assert RemoteRemediationExecutor(context).execute(action) is False

    assert action.execution_status == "NOT_EXECUTED"


def test_connection_loss_does_not_change_action_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action("connection-identity")
    action.authorize()

    original_id = action.action_id

    session.disconnect()

    assert RemoteRemediationExecutor(context).execute(action) is False
    assert action.action_id == original_id


def test_connection_loss_does_not_change_session_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    original_session_id = session.session_id

    session.disconnect()

    assert RemoteRemediationExecutor(context).execute(
        make_action("connection-session")
    ) is False

    assert session.session_id == original_session_id


def test_failed_verification_does_not_resolve_workflow():
    workflow = prepare_workflow_for_verification()

    result = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="verification-failure",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING
    assert workflow.is_terminal is False


def test_failed_verification_preserves_workflow_history():
    workflow = prepare_workflow_for_verification()

    history_before = workflow.history

    RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="history-preservation",
    )

    assert workflow.history == history_before


def test_failed_verification_can_be_followed_by_recovery():
    workflow = prepare_workflow_for_verification()

    result = RemediationVerifier().verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="recovery-verification",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING

    workflow._transition_to(WorkflowState.REMEDIATING)
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_recovery_preserves_original_workflow_history():
    workflow = prepare_workflow_for_verification()

    original_history = workflow.history

    workflow._transition_to(WorkflowState.REMEDIATING)
    workflow.start_verification()
    workflow.resolve()

    history = workflow.history

    assert history[:5] == original_history
    assert len(history) == 8


def test_recovery_reopen_preserves_complete_history():
    workflow = prepare_workflow_for_verification()

    workflow._transition_to(WorkflowState.REMEDIATING)
    workflow.start_verification()
    workflow.resolve()
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False
    assert len(workflow.history) == 9


def test_remote_diagnostic_failure_boundary_preserves_connection():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(machine, session)

    result = RemoteDiagnosticPipeline().diagnose(remote_input)

    assert result["machine_id"] == machine.machine_id
    assert result["session_id"] == session.session_id
    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_diagnostic_repeated_after_failure_boundary_is_stable():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    first = pipeline.diagnose(remote_input)
    second = pipeline.diagnose(remote_input)

    assert first["machine_id"] == second["machine_id"]
    assert first["session_id"] == second["session_id"]
    assert first["is_remote"] is True
    assert second["is_remote"] is True


def test_proactive_dismissal_does_not_mutate_machine_connection():
    machine = make_machine()
    recommendation = make_proactive_recommendation(machine)

    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert machine.connection_state == "UNKNOWN"


def test_proactive_resolution_does_not_execute_remediation():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is high.",
    )

    alert.resolve()

    assert alert.status == "RESOLVED"
    assert machine.connection_state == "UNKNOWN"


def test_proactive_case_failure_boundary_preserves_machine_identity():
    machine = make_machine()

    recommendation = make_proactive_recommendation(machine)
    case = ProactiveCaseCreator().create(recommendation)

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert machine.connection_state == "UNKNOWN"


def test_multiple_failed_actions_remain_isolated():
    actions = [
        make_failing_action(f"failure-{index}")
        for index in range(25)
    ]

    for action in actions:
        action.authorize()
        assert action.execute() is False

    assert all(
        action.execution_status == "FAILED"
        for action in actions
    )

    assert len({
        action.action_id
        for action in actions
    }) == 25


def test_failed_actions_do_not_affect_each_other():
    failing = make_failing_action("failing")
    successful = make_action("successful")

    failing.authorize()
    successful.authorize()

    assert failing.execute() is False
    assert successful.execute() is True

    assert failing.execution_status == "FAILED"
    assert successful.execution_status == "EXECUTED"


def test_repeated_failure_recovery_operations_remain_bounded():
    start = time.perf_counter()

    for index in range(100):
        action = make_failing_action(f"bounded-{index}")
        action.authorize()

        assert action.execute() is False
        assert action.execute() is False

    elapsed = time.perf_counter() - start

    assert elapsed < 5.0