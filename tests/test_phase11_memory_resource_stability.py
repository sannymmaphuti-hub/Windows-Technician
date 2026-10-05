import gc
import time
import weakref

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


def make_remote_input(machine, session, observations=None):
    if observations is None:
        observations = [make_observation()]

    return RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(machine, session),
        observations=observations,
    )


def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Memory stability operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Memory stability action",
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


def test_history_property_does_not_expose_internal_list():
    workflow = make_workflow()

    workflow.start_investigation()

    history_a = workflow.history
    history_b = workflow.history

    assert history_a is not history_b
    assert history_a == history_b


def test_repeated_history_reads_do_not_change_history_length():
    workflow = make_workflow()

    workflow.start_investigation()
    original_length = len(workflow.history)

    for _ in range(1000):
        assert len(workflow.history) == original_length

    assert len(workflow.history) == original_length


def test_remote_observation_collection_does_not_grow_on_repeated_reads():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    for _ in range(1000):
        observations = remote_input.observations
        assert len(observations) == 1

    assert len(remote_input.observations) == 1


def test_remote_observation_collection_returns_independent_lists():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    first = remote_input.observations
    second = remote_input.observations

    assert first is not second

    first.clear()

    assert len(second) == 1
    assert len(remote_input.observations) == 1


def test_observation_evidence_creation_does_not_mutate_observation():
    observation = make_observation()

    for _ in range(1000):
        evidence = observation.to_evidence()
        evidence["value"] = "mutated"

    assert observation.value == "warning"


def test_repeated_diagnostic_runs_do_not_accumulate_input_observations():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    for _ in range(50):
        pipeline.diagnose(remote_input)

    assert len(remote_input.observations) == 1


def test_repeated_diagnostic_runs_preserve_machine_state():
    machine = make_machine()
    session = make_session(machine)
    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    for _ in range(50):
        pipeline.diagnose(remote_input)

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_workflow_history_grows_only_when_transition_occurs():
    workflow = make_workflow()

    assert workflow.history == []

    workflow.start_investigation()

    assert len(workflow.history) == 1

    workflow.mark_diagnosed()

    assert len(workflow.history) == 2


def test_failed_transition_does_not_grow_history():
    workflow = make_workflow()

    for _ in range(100):
        try:
            workflow.mark_diagnosed()
        except ValueError:
            pass

    assert workflow.history == []
    assert workflow.state is WorkflowState.OPEN


def test_repeated_failed_action_attempts_do_not_grow_execution_state():
    calls = []

    def handler():
        calls.append("attempt")
        raise RuntimeError("resource test failure")

    action = make_action("resource-failure", handler)
    action.authorize()

    for _ in range(1000):
        assert action.execute() is False

    assert calls == ["attempt"]
    assert action.execution_status == "FAILED"
    assert action.failure_reason == "resource test failure"


def test_repeated_successful_action_attempts_do_not_grow_execution_state():
    calls = []

    def handler():
        calls.append("attempt")

    action = make_action("resource-success", handler)
    action.authorize()

    for _ in range(1000):
        action.execute()

    assert calls == ["attempt"]
    assert action.execution_status == "EXECUTED"


def test_repeated_verification_does_not_accumulate_state():
    verifier = RemediationVerifier()

    expected = {"status": "healthy"}
    observed = {"status": "healthy"}

    results = []

    for _ in range(1000):
        result = verifier.verify(
            expected=expected,
            observed=observed,
            action_id="resource-verification",
        )
        results.append(result.verification_result)

    assert all(
        result == results[0]
        for result in results
    )

    assert results[0]["expected"] is expected
    assert results[0]["observed"] is observed


def test_proactive_case_creation_does_not_change_machine_state():
    machine = make_machine()

    for _ in range(100):
        recommendation = make_proactive_recommendation(machine)
        case = ProactiveCaseCreator().create(recommendation)

        assert case.machine_id == machine.machine_id
        assert case.hostname == machine.hostname

    assert machine.connection_state == "UNKNOWN"
    assert machine.health_state == "UNKNOWN"


def test_multiple_remote_sessions_do_not_share_machine_state():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(50)
    ]

    sessions = [
        make_session(machine)
        for machine in machines
    ]

    sessions[0].disconnect()

    assert machines[0].connection_state == "DISCONNECTED"

    assert all(
        machine.connection_state == "CONNECTED"
        for machine in machines[1:]
    )


def test_multiple_workflows_do_not_share_history():
    workflows = [
        make_workflow()
        for _ in range(50)
    ]

    workflows[0].start_investigation()

    assert len(workflows[0].history) == 1

    assert all(
        workflow.history == []
        for workflow in workflows[1:]
    )


def test_multiple_actions_do_not_share_operation_state():
    actions = [
        make_action(f"action-{index}")
        for index in range(50)
    ]

    for action in actions:
        action.authorize()

    actions[0].execute()

    assert actions[0].execution_status == "EXECUTED"

    assert all(
        action.execution_status == "NOT_EXECUTED"
        for action in actions[1:]
    )


def test_remote_executor_does_not_retain_extra_machine_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action("retention-action")
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert context.machine_id == machine.machine_id
    assert context.session_id == session.session_id


def test_temporary_diagnostic_objects_can_be_collected():
    def create_objects():
        machine = make_machine("temporary")
        session = make_session(machine)
        remote_input = make_remote_input(machine, session)
        pipeline = RemoteDiagnosticPipeline()

        pipeline.diagnose(remote_input)

        return weakref.ref(machine), weakref.ref(session)

    machine_ref, session_ref = create_objects()

    gc.collect()

    assert machine_ref() is None
    assert session_ref() is None


def test_temporary_workflow_objects_can_be_collected():
    def create_workflow():
        workflow = make_workflow()
        workflow.start_investigation()
        return weakref.ref(workflow)

    workflow_ref = create_workflow()

    gc.collect()

    assert workflow_ref() is None


def test_temporary_action_objects_can_be_collected():
    def create_action():
        action = make_action("temporary-action")
        action.authorize()
        action.execute()
        return weakref.ref(action)

    action_ref = create_action()

    gc.collect()

    assert action_ref() is None


def test_repeated_temporary_object_creation_remains_bounded():
    start = time.perf_counter()

    for index in range(500):
        machine = make_machine(f"bounded-{index}")
        session = make_session(machine)
        remote_input = make_remote_input(machine, session)

        RemoteDiagnosticPipeline().diagnose(remote_input)

        action = make_action(f"bounded-action-{index}")
        action.authorize()
        action.execute()

        workflow = make_workflow()
        workflow.start_investigation()

    gc.collect()

    elapsed = time.perf_counter() - start

    assert elapsed < 10.0