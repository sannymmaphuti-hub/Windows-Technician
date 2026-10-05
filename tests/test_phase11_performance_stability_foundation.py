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


def make_session(machine):
    session = RemoteSession(machine)
    session.connect()
    return session


def make_observation():
    return Observation(
        source="system",
        subject="network",
        attribute="status",
        value="warning",
    )


def make_remote_input(machine, session):
    context = RemoteDiagnosticContext(machine, session)

    return RemoteDiagnosticInput(
        context=context,
        observations=[make_observation()],
    )


def make_action(action_id="action-1", handler=None):
    if handler is None:
        handler = lambda: None

    operation = RemediationOperation(
        operation_id=f"operation-{action_id}",
        description="Performance test operation",
        handler=handler,
    )

    return RemediationAction(
        action_id=action_id,
        description="Performance test action",
        requires_authorization=True,
        operation=operation,
    )

def make_workflow():
    return TechnicianWorkflow(DiagnosticCase())

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
    return ProactiveCaseCreator().create(
        make_proactive_recommendation(machine)
    )


# ---------------------------------------------------------------------------
# Object creation stability
# ---------------------------------------------------------------------------

def test_managed_machine_creation_is_deterministic():
    machine = make_machine()

    assert machine.machine_id == "machine-1"
    assert machine.hostname == "HOST-machine-1"
    assert machine.platform == "Windows"
    assert machine.operating_system == "Windows 11"
    assert machine.connection_state == "UNKNOWN"
    assert machine.health_state == "UNKNOWN"
    assert machine.last_seen is None


def test_remote_session_creation_is_deterministic():
    machine = make_machine()
    session = RemoteSession(machine)

    assert session.machine is machine
    assert session.state == "DISCONNECTED"
    assert session.session_id


def test_diagnostic_case_creation_is_deterministic():
    case = DiagnosticCase()

    assert case.case_id
    assert case.status == "NORMAL"


def test_workflow_creation_is_deterministic():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    assert workflow.case is case
    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False
    assert workflow.history == []


def test_action_creation_is_deterministic():
    action = make_action()

    assert action.action_id == "action-1"
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_observation_creation_is_deterministic():
    observation = make_observation()

    evidence = observation.to_evidence()

    assert evidence == {
        "source": "system",
        "subject": "network",
        "attribute": "status",
        "value": "warning",
    }


# ---------------------------------------------------------------------------
# Identity stability
# ---------------------------------------------------------------------------

def test_machine_ids_are_unique():
    machines = [
        make_machine(f"machine-{index}")
        for index in range(50)
    ]

    machine_ids = [machine.machine_id for machine in machines]

    assert len(machine_ids) == len(set(machine_ids))


def test_remote_session_ids_are_unique():
    sessions = []

    for index in range(50):
        machine = make_machine(f"machine-{index}")
        sessions.append(RemoteSession(machine))

    session_ids = [session.session_id for session in sessions]

    assert len(session_ids) == len(set(session_ids))


def test_case_ids_are_unique():
    cases = [DiagnosticCase() for _ in range(50)]

    case_ids = [case.case_id for case in cases]

    assert len(case_ids) == len(set(case_ids))


def test_workflow_ids_are_unique():
    workflows = [
        TechnicianWorkflow(DiagnosticCase())
        for _ in range(50)
    ]

    workflow_ids = [workflow.workflow_id for workflow in workflows]

    assert len(workflow_ids) == len(set(workflow_ids))


# ---------------------------------------------------------------------------
# State isolation under repeated creation
# ---------------------------------------------------------------------------

def test_repeated_machine_creation_does_not_share_state():
    machine_a = make_machine("machine-a")
    machine_b = make_machine("machine-b")

    machine_a.connection_state = "CONNECTED"

    assert machine_a.connection_state == "CONNECTED"
    assert machine_b.connection_state == "UNKNOWN"


def test_repeated_case_creation_does_not_share_state():
    case_a = DiagnosticCase()
    case_b = DiagnosticCase()

    case_a.status = "CUSTOM"

    assert case_a.status == "CUSTOM"
    assert case_b.status == "NORMAL"


def test_repeated_workflow_creation_does_not_share_history():
    workflow_a = TechnicianWorkflow(DiagnosticCase())
    workflow_b = TechnicianWorkflow(DiagnosticCase())

    workflow_a.start_investigation()

    assert len(workflow_a.history) == 1
    assert workflow_b.history == []
    assert workflow_b.state is WorkflowState.OPEN


def test_repeated_action_creation_does_not_share_authorization():
    action_a = make_action("action-a")
    action_b = make_action("action-b")

    action_a.authorize()

    assert action_a.authorization_status == "AUTHORIZED"
    assert action_b.authorization_status == "UNAUTHORIZED"


# ---------------------------------------------------------------------------
# Remote lifecycle stability
# ---------------------------------------------------------------------------

def test_connect_is_idempotent():
    machine = make_machine()
    session = RemoteSession(machine)

    session.connect()
    first_session_id = session.session_id

    session.connect()

    assert session.state == "CONNECTED"
    assert session.session_id == first_session_id
    assert machine.connection_state == "CONNECTED"


def test_disconnect_is_idempotent():
    machine = make_machine()
    session = make_session(machine)

    session.disconnect()
    session.disconnect()

    assert session.state == "DISCONNECTED"
    assert machine.connection_state == "DISCONNECTED"


def test_reconnect_preserves_session_identity():
    machine = make_machine()
    session = make_session(machine)

    original_session_id = session.session_id

    session.disconnect()
    session.connect()

    assert session.session_id == original_session_id
    assert session.state == "CONNECTED"


def test_remote_context_preserves_identity():
    machine = make_machine()
    session = make_session(machine)

    context = RemoteDiagnosticContext(machine, session)

    assert context.machine_id == machine.machine_id
    assert context.hostname == machine.hostname
    assert context.session_id == session.session_id
    assert context.is_remote is True


# ---------------------------------------------------------------------------
# Diagnostic repeatability
# ---------------------------------------------------------------------------

def test_remote_diagnostic_input_copies_observation_collection():
    machine = make_machine()
    session = make_session(machine)

    observations = [make_observation()]

    remote_input = RemoteDiagnosticInput(
        context=RemoteDiagnosticContext(machine, session),
        observations=observations,
    )

    observations.append(
        Observation(
            source="system",
            subject="cpu",
            attribute="usage",
            value=90,
        )
    )

    assert len(remote_input.observations) == 1


def test_remote_diagnostic_pipeline_returns_consistent_identity():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(machine, session)

    pipeline = RemoteDiagnosticPipeline()

    result_a = pipeline.diagnose(remote_input)
    result_b = pipeline.diagnose(remote_input)

    assert result_a["machine_id"] == result_b["machine_id"]
    assert result_a["hostname"] == result_b["hostname"]
    assert result_a["session_id"] == result_b["session_id"]
    assert result_a["is_remote"] is True
    assert result_b["is_remote"] is True


def test_remote_diagnostic_does_not_mutate_machine_connection_state():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(machine, session)

    RemoteDiagnosticPipeline().diagnose(remote_input)

    assert session.state == "CONNECTED"
    assert machine.connection_state == "CONNECTED"


def test_remote_diagnostic_does_not_execute_action():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(machine, session)
    action = make_action()

    RemoteDiagnosticPipeline().diagnose(remote_input)

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


# ---------------------------------------------------------------------------
# Proactive stability
# ---------------------------------------------------------------------------

def test_proactive_alert_creation_is_deterministic():
    machine = make_machine()

    alert = ProactiveAlert(
        machine=machine,
        alert_type="CPU_ANOMALY",
        metric="cpu_usage",
        message="CPU usage is unusually high.",
    )

    assert alert.machine_id == machine.machine_id
    assert alert.hostname == machine.hostname
    assert alert.status == "ACTIVE"


def test_proactive_recommendation_creation_is_deterministic():
    machine = make_machine()
    recommendation = make_proactive_recommendation(machine)

    assert recommendation.machine_id == machine.machine_id
    assert recommendation.hostname == machine.hostname
    assert recommendation.status == "PENDING"


def test_proactive_case_creation_is_deterministic():
    machine = make_machine()

    case = make_proactive_case(machine)

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname
    assert case.proactive_recommendation
    assert case.proactive_alert


def test_proactive_lifecycle_is_repeatable():
    machine = make_machine()
    recommendation = make_proactive_recommendation(machine)

    recommendation.acknowledge()
    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"


def test_proactive_lifecycle_does_not_connect_machine():
    machine = make_machine()
    recommendation = make_proactive_recommendation(machine)

    recommendation.acknowledge()
    recommendation.dismiss()

    assert machine.connection_state == "UNKNOWN"


# ---------------------------------------------------------------------------
# Remediation stability
# ---------------------------------------------------------------------------

def test_action_authorization_is_idempotent():
    action = make_action()

    action.authorize()
    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_action_deny_is_idempotent():
    action = make_action()

    action.deny()
    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"


def test_successful_action_executes_once():
    calls = []

    def handler():
        calls.append("executed")

    action = make_action("once", handler)
    action.authorize()

    assert action.execute() is True
    assert action.execute() is False

    assert calls == ["executed"]
    assert action.execution_status == "EXECUTED"


def test_failed_action_executes_once():
    calls = []

    def handler():
        calls.append("executed")
        raise RuntimeError("performance test failure")

    action = make_action("failed-once", handler)
    action.authorize()

    assert action.execute() is False
    assert action.execute() is False

    assert calls == ["executed"]
    assert action.execution_status == "FAILED"


def test_verifier_is_deterministic_for_matching_state():
    verifier = RemediationVerifier()

    result_a = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "healthy"},
        action_id="action-1",
    )

    result_b = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "healthy"},
        action_id="action-1",
    )

    assert result_a.verification_result == result_b.verification_result


def test_verifier_is_deterministic_for_mismatched_state():
    verifier = RemediationVerifier()

    result_a = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    result_b = verifier.verify(
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
        action_id="action-1",
    )

    assert result_a.verification_result == result_b.verification_result


# ---------------------------------------------------------------------------
# Remote remediation stability
# ---------------------------------------------------------------------------

def test_remote_executor_preserves_action_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action("remote-action")
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is True
    assert action.action_id == "remote-action"


def test_remote_executor_does_not_change_machine_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action()
    action.authorize()

    RemoteRemediationExecutor(context).execute(action)

    assert context.machine_id == machine.machine_id
    assert session.machine.machine_id == machine.machine_id


def test_remote_executor_does_not_change_session_identity():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    original_session_id = session.session_id

    action = make_action()
    action.authorize()

    RemoteRemediationExecutor(context).execute(action)

    assert session.session_id == original_session_id
    assert context.session_id == original_session_id


def test_remote_executor_failure_is_stable():
    machine = make_machine()
    session = make_session(machine)
    context = RemoteRemediationContext(machine, session)

    action = make_action(
        "remote-failure",
        lambda: (_ for _ in ()).throw(
            RuntimeError("remote failure")
        ),
    )
    action.authorize()

    executor = RemoteRemediationExecutor(context)

    assert executor.execute(action) is False
    assert executor.execute(action) is False

    assert action.execution_status == "FAILED"


# ---------------------------------------------------------------------------
# Workflow stability
# ---------------------------------------------------------------------------

def test_workflow_history_grows_only_on_valid_transitions():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    assert len(workflow.history) == 3


def test_invalid_transition_does_not_mutate_state():
    workflow = make_workflow()

    try:
        workflow.mark_diagnosed()
    except ValueError:
        pass

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


def test_invalid_transition_does_not_append_history():
    workflow = make_workflow()

    try:
        workflow.start_remediation()
    except ValueError:
        pass

    assert workflow.history == []


def test_resolution_is_stable():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_reopen_is_stable():
    workflow = make_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()
    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False


# ---------------------------------------------------------------------------
# Collection / history stability
# ---------------------------------------------------------------------------

def test_workflow_history_returns_a_copy():
    workflow = make_workflow()

    workflow.start_investigation()

    history = workflow.history
    history.clear()

    assert len(workflow.history) == 1


def test_observation_evidence_returns_independent_dictionary():
    observation = make_observation()

    evidence = observation.to_evidence()
    evidence["value"] = "changed"

    assert observation.value == "warning"


def test_remote_input_observations_are_not_exposed_as_mutable_internal_list():
    machine = make_machine()
    session = make_session(machine)

    remote_input = make_remote_input(machine, session)

    observations = remote_input.observations

    observations.clear()

    assert len(remote_input.observations) == 1


# ---------------------------------------------------------------------------
# Moderate repeatability workload
# ---------------------------------------------------------------------------

def test_repeated_case_creation_completes_within_reasonable_time():
    start = time.perf_counter()

    cases = [DiagnosticCase() for _ in range(500)]

    elapsed = time.perf_counter() - start

    assert len(cases) == 500
    assert elapsed < 2.0


def test_repeated_machine_creation_completes_within_reasonable_time():
    start = time.perf_counter()

    machines = [
        make_machine(f"machine-{index}")
        for index in range(500)
    ]

    elapsed = time.perf_counter() - start

    assert len(machines) == 500
    assert elapsed < 2.0


def test_repeated_action_creation_completes_within_reasonable_time():
    start = time.perf_counter()

    actions = [
        make_action(f"action-{index}")
        for index in range(500)
    ]

    elapsed = time.perf_counter() - start

    assert len(actions) == 500
    assert elapsed < 2.0


def test_repeated_workflow_creation_completes_within_reasonable_time():
    start = time.perf_counter()

    workflows = [
        TechnicianWorkflow(DiagnosticCase())
        for _ in range(500)
    ]

    elapsed = time.perf_counter() - start

    assert len(workflows) == 500
    assert elapsed < 2.0


def test_repeated_observation_creation_completes_within_reasonable_time():
    start = time.perf_counter()

    observations = [
        Observation(
            source="system",
            subject="network",
            attribute="status",
            value="warning",
        )
        for _ in range(500)
    ]

    elapsed = time.perf_counter() - start

    assert len(observations) == 500
    assert elapsed < 2.0