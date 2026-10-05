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
    context = RemoteDiagnosticContext(machine, session)

    return RemoteDiagnosticInput(
        context=context,
        observations=[make_observation()],
    )


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Lifecycle stress operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Lifecycle stress action",
        requires_authorization=True,
        operation=operation,
    )


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


def test_repeated_remote_session_lifecycle_preserves_identity():
    machine = make_machine()
    session = RemoteSession(machine)

    original_session_id = session.session_id

    for _ in range(100):
        session.connect()
        assert session.state == "CONNECTED"
        assert machine.connection_state == "CONNECTED"

        session.disconnect()
        assert session.state == "DISCONNECTED"
        assert machine.connection_state == "DISCONNECTED"

    session.connect()

    assert session.session_id == original_session_id
    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_repeated_remote_session_lifecycle_does_not_create_new_identity():
    machine = make_machine()
    session = RemoteSession(machine)

    original_session_id = session.session_id

    for _ in range(100):
        session.connect()
        session.connect()
        session.disconnect()
        session.disconnect()

    assert session.session_id == original_session_id
    assert session.state == "DISCONNECTED"


def test_multiple_machines_keep_remote_session_state_isolated():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(25)
    ]

    sessions = [
        RemoteSession(machine)
        for machine in machines
    ]

    for session in sessions:
        session.connect()

    assert all(session.state == "CONNECTED" for session in sessions)
    assert all(
        machine.connection_state == "CONNECTED"
        for machine in machines
    )

    sessions[0].disconnect()

    assert sessions[0].state == "DISCONNECTED"
    assert machines[0].connection_state == "DISCONNECTED"

    assert all(
        session.state == "CONNECTED"
        for session in sessions[1:]
    )
    assert all(
        machine.connection_state == "CONNECTED"
        for machine in machines[1:]
    )


def test_repeated_workflow_recovery_lifecycle_preserves_history():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    first_history = workflow.history

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_history = workflow.history

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True
    assert len(first_history) == 6
    assert len(second_history) == 12


def test_repeated_workflow_reopen_cycles_preserve_history():
    workflow = make_workflow()

    workflow.start_investigation()

    for _ in range(10):
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()
        workflow.start_verification()
        workflow.resolve()

        assert workflow.state is WorkflowState.RESOLVED

        workflow.reopen()

        assert workflow.state is WorkflowState.INVESTIGATING

    assert len(workflow.history) == 61
    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False

def test_workflow_history_order_remains_correct_after_recovery():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()
    workflow.reopen()

    history = workflow.history

    expected = [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
        (WorkflowState.DIAGNOSED, WorkflowState.ACTION_REQUIRED),
        (WorkflowState.ACTION_REQUIRED, WorkflowState.REMEDIATING),
        (WorkflowState.REMEDIATING, WorkflowState.VERIFYING),
        (WorkflowState.VERIFYING, WorkflowState.RESOLVED),
        (WorkflowState.RESOLVED, WorkflowState.INVESTIGATING),
    ]

    assert history == expected


def test_repeated_authorization_attempts_do_not_change_execution_state():
    action = make_action()

    for _ in range(100):
        action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_repeated_execution_attempts_execute_successful_action_once():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("stress-success", handler)
    action.authorize()

    for _ in range(100):
        action.execute()

    assert calls == ["executed"]
    assert action.execution_status == "EXECUTED"


def test_repeated_execution_attempts_execute_failed_action_once():
    calls = []

    def handler():
        calls.append("executed")
        raise RuntimeError("stress failure")

    action = make_action("stress-failure", handler)
    action.authorize()

    for _ in range(100):
        action.execute()

    assert calls == ["executed"]
    assert action.execution_status == "FAILED"
    assert action.failure_reason == "stress failure"


def test_multiple_actions_keep_execution_state_isolated():
    actions = [
        make_action(f"action-{index}")
        for index in range(25)
    ]

    for action in actions:
        action.authorize()

    assert all(
        action.authorization_status == "AUTHORIZED"
        for action in actions
    )

    actions[0].execute()

    assert actions[0].execution_status == "EXECUTED"
    assert all(
        action.execution_status == "NOT_EXECUTED"
        for action in actions[1:]
    )


def test_repeated_remote_diagnostic_runs_preserve_connection():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    original_session_id = session.session_id

    for _ in range(25):
        result = pipeline.diagnose(remote_input)

        assert result["machine_id"] == machine.machine_id
        assert result["session_id"] == original_session_id
        assert result["is_remote"] is True
        assert session.state == "CONNECTED"
        assert machine.connection_state == "CONNECTED"


def test_repeated_remote_diagnostic_runs_do_not_change_observation_count():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    original_count = len(remote_input.observations)

    for _ in range(25):
        pipeline.diagnose(remote_input)

    assert len(remote_input.observations) == original_count


def test_remote_remediation_repeated_execution_is_stable():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    calls = []

    def handler():
        calls.append("executed")

    action = make_action("remote-stress", handler)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    results = [
        executor.execute(action)
        for _ in range(100)
    ]

    assert results[0] is True
    assert all(result is False for result in results[1:])
    assert calls == ["executed"]
    assert action.execution_status == "EXECUTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_remediation_failure_remains_stable():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    calls = []

    def handler():
        calls.append("executed")
        raise RuntimeError("remote lifecycle failure")

    action = make_action("remote-failed", handler)
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    for _ in range(100):
        assert executor.execute(action) is False

    assert calls == ["executed"]
    assert action.execution_status == "FAILED"
    assert action.failure_reason == "remote lifecycle failure"


def test_proactive_lifecycle_repetition_preserves_machine_state():
    machine = make_machine()
    recommendation = make_proactive_recommendation(machine)

    for _ in range(100):
        recommendation.acknowledge()

    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"
    assert machine.connection_state == "UNKNOWN"
    assert machine.health_state == "UNKNOWN"


def test_proactive_case_creation_repeatedly_preserves_machine_identity():
    machine = make_machine()

    cases = []

    for _ in range(50):
        recommendation = make_proactive_recommendation(machine)
        case = ProactiveCaseCreator().create(recommendation)
        cases.append(case)

    assert len(cases) == 50
    assert all(
        case.machine_id == machine.machine_id
        for case in cases
    )
    assert all(
        case.hostname == machine.hostname
        for case in cases
    )


def test_verification_repetition_is_deterministic():
    verifier = RemediationVerifier()

    results = []

    for _ in range(100):
        result = verifier.verify(
            expected={"status": "healthy"},
            observed={"status": "healthy"},
            action_id="verification-stress",
        )
        results.append(result.verification_result)

    assert all(
        result == results[0]
        for result in results
    )


def test_verification_mismatch_repetition_is_deterministic():
    verifier = RemediationVerifier()

    results = []

    for _ in range(100):
        result = verifier.verify(
            expected={"status": "healthy"},
            observed={"status": "unhealthy"},
            action_id="verification-stress",
        )
        results.append(result.verification_result)

    assert all(
        result == results[0]
        for result in results
    )


def test_mixed_machine_case_workflow_creation_remains_isolated():
    records = []

    for index in range(50):
        machine = make_machine(f"mixed-{index}")
        case = DiagnosticCase()
        case.machine_id = machine.machine_id
        case.hostname = machine.hostname

        workflow = TechnicianWorkflow(case)

        records.append((machine, case, workflow))

    for index, (machine, case, workflow) in enumerate(records):
        assert machine.machine_id == f"mixed-{index}"
        assert case.machine_id == machine.machine_id
        assert case.hostname == machine.hostname
        assert workflow.case is case
        assert workflow.state is WorkflowState.OPEN
        assert workflow.history == []


def test_lifecycle_stress_workload_completes_within_reasonable_time():
    start = time.perf_counter()

    for index in range(100):
        machine = make_machine(f"stress-{index}")
        session = make_session(machine)

        remote_input = make_remote_input(machine, session)

        RemoteDiagnosticPipeline().diagnose(remote_input)

        action = make_action(f"stress-action-{index}")
        action.authorize()

        RemoteRemediationExecutor(
            RemoteRemediationContext(machine, session)
        ).execute(action)

        workflow = make_workflow()
        workflow.start_investigation()
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()
        workflow.start_verification()
        workflow.resolve()
        workflow.reopen()

    elapsed = time.perf_counter() - start

    assert elapsed < 10.0