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


def make_observation(subject="network", value="warning"):
    return Observation(
        source="system",
        subject=subject,
        attribute="status",
        value=value,
    )


def make_remote_input(
    machine,
    session,
    subject="network",
    value="warning",
):
    return RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(machine, session),
        observations=[
            make_observation(subject, value),
        ],
    )


def make_workflow(machine):
    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname

    return TechnicianWorkflow(case)


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Long-running stability operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Long-running stability action",
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


def complete_workflow_to_resolved(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def test_repeated_remote_diagnostics_do_not_accumulate_observations():
    machine = make_machine()
    session = make_session(machine)
    pipeline = RemoteDiagnosticPipeline()

    results = []

    for _ in range(100):
        remote_input = make_remote_input(machine, session)
        results.append(
            pipeline.diagnose(remote_input)
        )

    assert len(results) == 100

    assert all(
        len(result["observations"]) == 1
        for result in results
    )

    assert all(
        result["machine_id"] == machine.machine_id
        for result in results
    )


def test_repeated_remote_diagnostics_preserve_machine_connection_state():
    machine = make_machine()
    session = make_session(machine)
    pipeline = RemoteDiagnosticPipeline()

    for _ in range(100):
        remote_input = make_remote_input(machine, session)
        pipeline.diagnose(remote_input)

        assert machine.connection_state == "CONNECTED"
        assert session.state == "CONNECTED"


def test_repeated_workflow_cycles_preserve_history():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow_to_resolved(workflow)

    first_history_length = len(workflow.history)

    for _ in range(25):
        workflow.reopen()
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()
        workflow.start_verification()
        workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED

    assert len(workflow.history) == (
        first_history_length + (25 * 6)
    )


def test_repeated_reopen_cycles_preserve_original_history():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow_to_resolved(workflow)

    original_history = workflow.history

    for _ in range(10):
        workflow.reopen()
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()
        workflow.start_verification()
        workflow.resolve()

    assert workflow.history[:6] == original_history
    assert len(workflow.history) == 66


def test_repeated_action_execution_does_not_repeat_completed_operation():
    execution_count = 0

    def handler():
        nonlocal execution_count
        execution_count += 1

    action = make_action(
        "repeat-safe",
        handler,
    )

    action.authorize()

    assert action.execute() is True

    for _ in range(100):
          assert action.execute() is False

    assert execution_count == 1
    assert action.execution_status == "EXECUTED"
    assert action.operation.execution_status == "EXECUTED"


def test_repeated_failed_action_execution_preserves_failure_state():
    execution_count = 0

    def handler():
        nonlocal execution_count
        execution_count += 1
        raise RuntimeError("intentional failure")

    action = make_action(
        "failed-repeat",
        handler,
    )

    action.authorize()

    assert action.execute() is False

    for _ in range(50):
          assert action.execute() is False

    assert execution_count == 1
    assert action.execution_status == "FAILED"
    assert action.operation.execution_status == "FAILED"
    assert action.failure_reason == "intentional failure"


def test_repeated_verification_preserves_verification_result():
    verifier = RemediationVerifier()

    expected = {"status": "healthy"}
    observed = {"status": "healthy"}

    first = verifier.verify(
        expected=expected,
        observed=observed,
        action_id="verification-1",
    )

    for _ in range(100):
        result = verifier.verify(
            expected=expected,
            observed=observed,
            action_id="verification-1",
        )

        assert result.verification_result == (
            first.verification_result
        )

    assert first.verification_result["verified"] is True


def test_repeated_verification_failure_remains_failure():
    verifier = RemediationVerifier()

    expected = {"status": "healthy"}
    observed = {"status": "unhealthy"}

    for _ in range(100):
        result = verifier.verify(
            expected=expected,
            observed=observed,
            action_id="verification-failure",
        )

        assert result.verification_result["verified"] is False


def test_failed_verification_does_not_resolve_workflow():
    machine = make_machine()
    workflow = make_workflow(machine)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="failed-verification",
    )

    assert result.verification_result["verified"] is False
    assert workflow.state is WorkflowState.VERIFYING

    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_repeated_remote_remediation_preserves_action_identity():
    machine = make_machine()
    session = make_session(machine)

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(context)

    actions = [
        make_action(f"remote-action-{index}")
        for index in range(20)
    ]

    for action in actions:
        action.authorize()
        assert executor.execute(action) is True

    assert all(
        action.execution_status == "EXECUTED"
        for action in actions
    )

    assert len({
        action.action_id
        for action in actions
    }) == 20


def test_remote_connection_recovery_does_not_change_action_execution_state():
    machine = make_machine()
    session = make_session(machine)

    action = make_action("connection-recovery")

    session.disconnect()

    assert machine.connection_state == "DISCONNECTED"
    assert action.execution_status == "NOT_EXECUTED"

    session.connect()

    assert machine.connection_state == "CONNECTED"
    assert action.execution_status == "NOT_EXECUTED"

    action.authorize()

    context = RemoteRemediationContext(
        machine,
        session,
    )

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.execution_status == "EXECUTED"


def test_repeated_proactive_case_creation_preserves_machine_identity():
    machine = make_machine()
    creator = ProactiveCaseCreator()

    recommendation = make_proactive_recommendation(machine)

    cases = [
        creator.create(recommendation)
        for _ in range(50)
    ]

    assert all(
        case.machine_id == machine.machine_id
        for case in cases
    )

    assert all(
        case.hostname == machine.hostname
        for case in cases
    )

    assert len({
        case.case_id
        for case in cases
    }) == 50


def test_proactive_case_creation_does_not_mutate_machine_state():
    machine = make_machine()
    creator = ProactiveCaseCreator()

    recommendation = make_proactive_recommendation(machine)

    machine.connection_state = "CONNECTED"
    machine.health_state = "WARNING"

    for _ in range(50):
        creator.create(recommendation)

    assert machine.connection_state == "CONNECTED"
    assert machine.health_state == "WARNING"


def test_remote_diagnostic_case_workflow_can_be_repeated_without_state_leak():
    machine = make_machine()
    session = make_session(machine)
    pipeline = RemoteDiagnosticPipeline()

    workflows = []

    for _ in range(20):
        remote_input = make_remote_input(
            machine,
            session,
            subject="network",
            value="warning",
        )

        result = pipeline.diagnose(remote_input)

        case = DiagnosticCase()
        case.machine_id = result["machine_id"]
        case.hostname = result["hostname"]

        workflow = TechnicianWorkflow(case)

        workflow.start_investigation()
        workflow.mark_diagnosed()

        workflows.append(workflow)

    assert len(workflows) == 20

    assert all(
        workflow.state is WorkflowState.DIAGNOSED
        for workflow in workflows
    )

    assert len({
        workflow.workflow_id
        for workflow in workflows
    }) == 20

    assert all(
        len(workflow.history) == 2
        for workflow in workflows
    )


def test_remote_diagnostic_remediation_verification_lifecycle_repeats_safely():
    machine = make_machine()
    session = make_session(machine)
    pipeline = RemoteDiagnosticPipeline()
    verifier = RemediationVerifier()

    for index in range(20):
        remote_input = make_remote_input(
            machine,
            session,
            subject="network",
            value="warning",
        )

        result = pipeline.diagnose(remote_input)

        case = DiagnosticCase()
        case.machine_id = result["machine_id"]
        case.hostname = result["hostname"]

        workflow = TechnicianWorkflow(case)

        workflow.start_investigation()
        workflow.mark_diagnosed()
        workflow.require_action()
        workflow.start_remediation()

        action = make_action(
            f"lifecycle-{index}"
        )

        action.authorize()

        context = RemoteRemediationContext(
            machine,
            session,
        )

        executor = RemoteRemediationExecutor(context)

        assert executor.execute(action) is True

        workflow.start_verification()

        verification = verifier.verify(
            expected={"status": "healthy"},
            observed={"status": "healthy"},
            action_id=action.action_id,
        )

        assert verification.verification_result["verified"] is True

        workflow.resolve()

        assert workflow.state is WorkflowState.RESOLVED
        assert action.execution_status == "EXECUTED"


def test_terminal_workflows_remain_terminal_until_explicit_reopen():
    machine = make_machine()
    workflow = make_workflow(machine)

    complete_workflow_to_resolved(workflow)

    assert workflow.is_terminal is True
    assert workflow.state is WorkflowState.RESOLVED

    for _ in range(25):
        assert workflow.is_terminal is True
        assert workflow.state is WorkflowState.RESOLVED

    workflow.reopen()

    assert workflow.is_terminal is False
    assert workflow.state is WorkflowState.INVESTIGATING


def test_multiple_long_running_workflows_remain_independent():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(5)
    ]

    workflows = [
        make_workflow(machine)
        for machine in machines
    ]

    for workflow in workflows:
        complete_workflow_to_resolved(workflow)

    for index in range(5):
        for _ in range(index + 1):
            workflows[index].reopen()
            workflows[index].mark_diagnosed()
            workflows[index].require_action()
            workflows[index].start_remediation()
            workflows[index].start_verification()
            workflows[index].resolve()

    for index, workflow in enumerate(workflows):
        expected_history_length = (
            6 + ((index + 1) * 6)
        )

        assert workflow.state is WorkflowState.RESOLVED
        assert len(workflow.history) == expected_history_length
        assert workflow.case.machine_id == f"machine-{index}"


def test_long_running_machine_session_lifecycle_preserves_identity():
    machine = make_machine("persistent-machine")
    session = make_session(machine)

    original_session_id = session.session_id
    original_machine_id = machine.machine_id

    for _ in range(50):
        session.disconnect()

        assert machine.connection_state == "DISCONNECTED"

        session.connect()

        assert machine.connection_state == "CONNECTED"

    assert machine.machine_id == original_machine_id
    assert session.session_id == original_session_id
    assert session.machine is machine


def test_long_running_cross_pillar_objects_keep_shared_machine_identity():
    machine = make_machine("shared-machine")
    session = make_session(machine)

    recommendation = make_proactive_recommendation(machine)

    proactive_case = ProactiveCaseCreator().create(
        recommendation
    )

    remote_input = make_remote_input(
        machine,
        session,
    )

    remote_result = RemoteDiagnosticPipeline().diagnose(
        remote_input
    )

    workflow = make_workflow(machine)

    assert recommendation.machine_id == machine.machine_id
    assert proactive_case.machine_id == machine.machine_id
    assert remote_input.machine_id == machine.machine_id
    assert remote_result["machine_id"] == machine.machine_id
    assert workflow.case.machine_id == machine.machine_id

    assert recommendation.hostname == machine.hostname
    assert proactive_case.hostname == machine.hostname
    assert remote_input.context.hostname == machine.hostname
    assert remote_result["hostname"] == machine.hostname
    assert workflow.case.hostname == machine.hostname