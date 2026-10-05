from concurrent.futures import ThreadPoolExecutor

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.observation import Observation
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_remediation_context import RemoteRemediationContext
from engine.remote_remediation_executor import RemoteRemediationExecutor
from engine.remote_session import RemoteSession
from engine.remediation_action import RemediationAction
from engine.remediation_operation import RemediationOperation
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


def make_machine(machine_id):
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


def make_observation(subject, value):
    return Observation(
        source="system",
        subject=subject,
        attribute="status",
        value=value,
    )


def make_remote_input(machine, session, subject, value):
    return RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(machine, session),
        observations=[
            make_observation(subject, value),
        ],
    )


def make_workflow(machine_id):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = f"HOST-{machine_id}"
    return TechnicianWorkflow(case)


def make_action(action_id):
    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description=f"Operation for {action_id}",
        handler=lambda: None,
    )

    return RemediationAction(
        action_id=action_id,
        description=f"Action for {action_id}",
        requires_authorization=True,
        operation=operation,
    )


def test_parallel_machines_keep_connection_state_isolated():
    machines = [
        make_machine("machine-1"),
        make_machine("machine-2"),
        make_machine("machine-3"),
        make_machine("machine-4"),
    ]

    sessions = [
        make_session(machine)
        for machine in machines
    ]

    assert all(
        machine.connection_state == "CONNECTED"
        for machine in machines
    )

    sessions[0].disconnect()

    assert machines[0].connection_state == "DISCONNECTED"
    assert machines[1].connection_state == "CONNECTED"
    assert machines[2].connection_state == "CONNECTED"
    assert machines[3].connection_state == "CONNECTED"


def test_parallel_remote_contexts_keep_machine_identity_isolated():
    machines = [
        make_machine("machine-1"),
        make_machine("machine-2"),
        make_machine("machine-3"),
    ]

    sessions = [
        make_session(machine)
        for machine in machines
    ]

    contexts = [
        RemoteDiagnosticContext(machine, session)
        for machine, session in zip(machines, sessions)
    ]

    assert [context.machine_id for context in contexts] == [
        "machine-1",
        "machine-2",
        "machine-3",
    ]

    assert [context.session_id for context in contexts] == [
        session.session_id
        for session in sessions
    ]


def test_parallel_remote_inputs_keep_observations_isolated():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    input_a = make_remote_input(
        machine_a,
        session_a,
        "network",
        "warning",
    )

    input_b = make_remote_input(
        machine_b,
        session_b,
        "memory",
        "critical",
    )

    assert input_a.machine_id == "machine-a"
    assert input_b.machine_id == "machine-b"

    assert input_a.observations[0].subject == "network"
    assert input_b.observations[0].subject == "memory"

    assert input_a.observations is not input_b.observations


def test_parallel_workflows_keep_history_isolated():
    workflows = [
        make_workflow(f"machine-{index}")
        for index in range(4)
    ]

    for workflow in workflows:
        workflow.start_investigation()
        workflow.mark_diagnosed()

    workflows[0].require_action()

    assert workflows[0].state is WorkflowState.ACTION_REQUIRED

    for workflow in workflows[1:]:
        assert workflow.state is WorkflowState.DIAGNOSED

    assert len(workflows[0].history) == 3

    for workflow in workflows[1:]:
        assert len(workflow.history) == 2


def test_parallel_actions_keep_execution_state_isolated():
    actions = [
        make_action(f"action-{index}")
        for index in range(4)
    ]

    actions[0].authorize()
    assert actions[0].execute() is True

    assert actions[0].execution_status == "EXECUTED"

    for action in actions[1:]:
        assert action.authorization_status == "UNAUTHORIZED"
        assert action.execution_status == "NOT_EXECUTED"


def test_parallel_actions_keep_authorization_state_isolated():
    actions = [
        make_action(f"action-{index}")
        for index in range(4)
    ]

    actions[0].authorize()
    actions[1].deny()

    assert actions[0].authorization_status == "AUTHORIZED"
    assert actions[1].authorization_status == "DENIED"

    assert actions[2].authorization_status == "UNAUTHORIZED"
    assert actions[3].authorization_status == "UNAUTHORIZED"


def test_remote_executor_does_not_cross_machine_boundaries():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    action_a = make_action("action-a")
    action_b = make_action("action-b")

    action_a.authorize()
    action_b.authorize()

    context_a = RemoteRemediationContext(machine_a, session_a)
    context_b = RemoteRemediationContext(machine_b, session_b)

    executor_a = RemoteRemediationExecutor(context_a)
    executor_b = RemoteRemediationExecutor(context_b)

    assert executor_a.context.machine_id == "machine-a"
    assert executor_b.context.machine_id == "machine-b"

    assert executor_a.execute(action_a) is True
    assert executor_b.execute(action_b) is True

    assert action_a.execution_status == "EXECUTED"
    assert action_b.execution_status == "EXECUTED"


def test_remote_session_disconnect_does_not_disconnect_other_machine():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    session_a.disconnect()

    assert session_a.state == "DISCONNECTED"
    assert machine_a.connection_state == "DISCONNECTED"

    assert session_b.state == "CONNECTED"
    assert machine_b.connection_state == "CONNECTED"


def test_parallel_diagnostic_inputs_do_not_share_machine_state():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    input_a = make_remote_input(
        machine_a,
        session_a,
        "network",
        "warning",
    )

    input_b = make_remote_input(
        machine_b,
        session_b,
        "memory",
        "critical",
    )

    pipeline = RemoteDiagnosticPipeline()

    result_a = pipeline.diagnose(input_a)
    result_b = pipeline.diagnose(input_b)

    assert result_a["machine_id"] == "machine-a"
    assert result_b["machine_id"] == "machine-b"

    assert result_a["hostname"] == "HOST-machine-a"
    assert result_b["hostname"] == "HOST-machine-b"

    assert result_a["observations"][0].subject == "network"
    assert result_b["observations"][0].subject == "memory"


def test_concurrent_workflow_creation_produces_independent_workflows():
    def create_and_transition(index):
        workflow = make_workflow(f"machine-{index}")
        workflow.start_investigation()
        workflow.mark_diagnosed()
        return workflow

    with ThreadPoolExecutor(max_workers=4) as executor:
        workflows = list(
            executor.map(create_and_transition, range(8))
        )

    assert len(workflows) == 8

    assert len({
        workflow.workflow_id
        for workflow in workflows
    }) == 8

    assert all(
        workflow.state is WorkflowState.DIAGNOSED
        for workflow in workflows
    )

    assert all(
        len(workflow.history) == 2
        for workflow in workflows
    )


def test_concurrent_action_execution_keeps_actions_independent():
    actions = [
        make_action(f"action-{index}")
        for index in range(8)
    ]

    for action in actions:
        action.authorize()

    def execute(action):
        return action.execute()

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(
            executor.map(execute, actions)
        )

    assert all(results)

    assert all(
        action.execution_status == "EXECUTED"
        for action in actions
    )

    assert len({
        action.action_id
        for action in actions
    }) == 8


def test_concurrent_machine_objects_do_not_share_health_state():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(6)
    ]

    machines[0].health_state = "WARNING"
    machines[1].health_state = "CRITICAL"

    assert machines[0].health_state == "WARNING"
    assert machines[1].health_state == "CRITICAL"

    for machine in machines[2:]:
        assert machine.health_state == "UNKNOWN"


def test_concurrent_case_objects_keep_case_identity_isolated():
    workflows = [
        make_workflow(f"machine-{index}")
        for index in range(6)
    ]

    case_ids = [
        workflow.case.case_id
        for workflow in workflows
    ]

    assert len(set(case_ids)) == 6

    machine_ids = [
        workflow.case.machine_id
        for workflow in workflows
    ]

    assert machine_ids == [
        f"machine-{index}"
        for index in range(6)
    ]


def test_parallel_sessions_have_unique_session_identity():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(6)
    ]

    sessions = [
        make_session(machine)
        for machine in machines
    ]

    session_ids = [
        session.session_id
        for session in sessions
    ]

    assert len(set(session_ids)) == 6


def test_parallel_operations_have_independent_execution_status():
    actions = [
        make_action(f"action-{index}")
        for index in range(5)
    ]

    actions[0].authorize()
    actions[0].execute()

    assert actions[0].operation.execution_status == "EXECUTED"

    for action in actions[1:]:
        assert action.operation.execution_status == "NOT_EXECUTED"


def test_parallel_workflow_transitions_do_not_modify_other_histories():
    workflows = [
        make_workflow(f"machine-{index}")
        for index in range(5)
    ]

    for workflow in workflows:
        workflow.start_investigation()

    histories_before = [
        workflow.history
        for workflow in workflows
    ]

    workflows[0].mark_diagnosed()
    workflows[1].escalate()

    assert len(workflows[0].history) == 2
    assert len(workflows[1].history) == 2

    for index in range(2, 5):
        assert workflows[index].history == histories_before[index]


def test_parallel_remote_contexts_reject_cross_machine_sessions():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    session_a = make_session(machine_a)
    session_b = make_session(machine_b)

    try:
        RemoteDiagnosticContext(machine_a, session_b)
        assert False, "Cross-machine diagnostic context should fail."
    except ValueError:
        pass

    try:
        RemoteRemediationContext(machine_b, session_a)
        assert False, "Cross-machine remediation context should fail."
    except ValueError:
        pass