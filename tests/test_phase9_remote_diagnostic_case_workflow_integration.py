from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.observation import Observation
from engine.remote_diagnostic_context import RemoteDiagnosticContext
from engine.remote_diagnostic_input import RemoteDiagnosticInput
from engine.remote_diagnostic_pipeline import RemoteDiagnosticPipeline
from engine.remote_session import RemoteSession
from engine.technician_workflow import TechnicianWorkflow


def create_remote_case_input():
    machine = __import__(
        "engine.managed_machine",
        fromlist=["ManagedMachine"],
    ).ManagedMachine(
        machine_id="machine-remote-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 10",
    )

    session = RemoteSession(machine)
    session.connect()

    context = RemoteDiagnosticContext(
        machine=machine,
        session=session,
    )

    observations = [
        Observation(
            source="network",
            subject="network_adapter",
            attribute="status",
            value="WARNING",
        )
    ]

    diagnostic_input = RemoteDiagnosticInput(
        context=context,
        observations=observations,
    )

    return machine, session, context, diagnostic_input


def diagnose_remote_case():
    machine, session, context, diagnostic_input = create_remote_case_input()

    pipeline = RemoteDiagnosticPipeline()
    result = pipeline.diagnose(diagnostic_input)

    case = DiagnosticCase()
    case.machine_id = machine.machine_id
    case.hostname = machine.hostname
    case.remote_session_id = session.session_id
    case.remote_diagnostic_result = result

    workflow = TechnicianWorkflow(case)

    return (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    )


def test_remote_input_contains_machine_identity():
    machine, session, context, diagnostic_input = create_remote_case_input()

    assert diagnostic_input.machine_id == machine.machine_id
    assert diagnostic_input.context.hostname == machine.hostname


def test_remote_input_contains_session_identity():
    machine, session, context, diagnostic_input = create_remote_case_input()

    assert diagnostic_input.session_id == session.session_id
    assert context.session_id == session.session_id


def test_remote_input_marks_remote_context():
    machine, session, context, diagnostic_input = create_remote_case_input()

    assert context.is_remote is True
    assert diagnostic_input.is_remote is True


def test_remote_input_preserves_observation_objects():
    machine, session, context, diagnostic_input = create_remote_case_input()

    assert len(diagnostic_input.observations) == 1
    assert isinstance(diagnostic_input.observations[0], Observation)


def test_remote_observation_contains_expected_source():
    machine, session, context, diagnostic_input = create_remote_case_input()

    observation = diagnostic_input.observations[0]

    assert observation.source == "network"


def test_remote_observation_contains_expected_subject():
    machine, session, context, diagnostic_input = create_remote_case_input()

    observation = diagnostic_input.observations[0]

    assert observation.subject == "network_adapter"


def test_remote_observation_contains_expected_attribute():
    machine, session, context, diagnostic_input = create_remote_case_input()

    observation = diagnostic_input.observations[0]

    assert observation.attribute == "status"


def test_remote_observation_contains_expected_value():
    machine, session, context, diagnostic_input = create_remote_case_input()

    observation = diagnostic_input.observations[0]

    assert observation.value == "WARNING"


def test_remote_pipeline_accepts_remote_input():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result is not None


def test_remote_pipeline_marks_result_as_remote():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result["is_remote"] is True


def test_remote_pipeline_preserves_machine_id():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result["machine_id"] == machine.machine_id


def test_remote_pipeline_preserves_hostname():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result["hostname"] == machine.hostname


def test_remote_pipeline_preserves_session_id():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result["session_id"] == session.session_id


def test_remote_pipeline_returns_observations():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert result["observations"] == diagnostic_input.observations


def test_remote_pipeline_produces_signals_collection():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert "signals" in result
    assert isinstance(result["signals"], list)


def test_remote_pipeline_produces_findings_collection():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert "findings" in result
    assert isinstance(result["findings"], list)


def test_remote_pipeline_produces_correlations_collection():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert "correlations" in result
    assert isinstance(result["correlations"], list)


def test_remote_pipeline_produces_root_cause_candidates():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert "candidates" in result
    assert isinstance(result["candidates"], list)


def test_remote_pipeline_produces_evaluations():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert "evaluations" in result
    assert isinstance(result["evaluations"], list)


def test_remote_case_preserves_machine_identity():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname


def test_remote_case_preserves_session_identity():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert case.remote_session_id == session.session_id


def test_remote_case_enters_technician_workflow():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    assert workflow.case is case
    assert workflow.state.value == "OPEN"


def test_remote_case_timeline_reads_from_workflow():
    (
        machine,
        session,
        context,
        diagnostic_input,
        result,
        case,
        workflow,
    ) = diagnose_remote_case()

    timeline = CaseTimeline(workflow)

    assert timeline.case is case
    assert timeline.case_id == case.case_id
    assert timeline.machine_id == machine.machine_id
    assert timeline.hostname == machine.hostname
    assert timeline.state.value == "OPEN"
    assert timeline.is_terminal is False