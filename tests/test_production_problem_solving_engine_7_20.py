import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import (
    ProductionProblemSolvingEngine,
    ProblemSolvingState,
)
from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.windows_diagnostic_result import WindowsDiagnosticResult
from engine.recommendation import Recommendation


def make_engine(dispatcher=None, coordinator=None):
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    return ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
        dispatcher=dispatcher,
        coordinator=coordinator,
    )


def make_result(recommendations=None):
    return WindowsDiagnosticResult(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        primary_cause=None,
        recommendations=recommendations or [],
        confidences=[],
    )


def high_recommendation():
    return Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority="HIGH",
        description="Review excessive memory consumption.",
        rationale="Memory pressure exceeds the configured threshold.",
    )


class FakeDispatcher:
    def __init__(self, results=None, failures=None):
        self.results = results or {}
        self.failures = failures or {}
        self.calls = []

    def dispatch(self, domain, evidence=None):
        self.calls.append(domain)

        if domain in self.failures:
            raise RuntimeError(self.failures[domain])

        return self.results.get(domain, make_result())


class FakeCoordinator:
    def __init__(self):
        self.calls = []

    def attach_result(self, case, result):
        self.calls.append((case, result))
        return result


# ============================================================
# 1. Multi-domain integration
# ============================================================

def test_7_20_all_domains_execute_through_single_dispatcher():
    dispatcher = FakeDispatcher()

    engine = make_engine(dispatcher=dispatcher)

    domains = [
        "PROCESS",
        "MEMORY",
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    ]

    execution = engine.execute_domains(domains)

    assert set(execution["results"]) == set(domains)
    assert execution["failures"] == {}
    assert dispatcher.calls == domains


def test_7_20_multi_domain_results_aggregate_to_one_canonical_result():
    dispatcher = FakeDispatcher(
        results={
            "PROCESS": make_result(),
            "MEMORY": make_result(),
            "NETWORK": make_result(),
        }
    )

    engine = make_engine(dispatcher=dispatcher)

    engine.workflow.start_investigation()

    engine.execute_domains(
        ["PROCESS", "MEMORY", "NETWORK"]
    )

    result = engine.aggregate_domain_results()

    assert isinstance(result, WindowsDiagnosticResult)
    assert isinstance(engine.result, WindowsDiagnosticResult)
    assert engine.workflow.state == WorkflowState.INVESTIGATING

    engine.workflow.mark_diagnosed()

    assert engine.workflow.state == WorkflowState.DIAGNOSED


# ============================================================
# 2. Partial diagnostic failure
# ============================================================

def test_7_20_partial_domain_failure_preserves_successes():
    dispatcher = FakeDispatcher(
        results={
            "PROCESS": make_result(),
            "MEMORY": make_result(),
        },
        failures={
            "NETWORK": "network unavailable",
        },
    )

    engine = make_engine(dispatcher=dispatcher)

    engine.workflow.start_investigation()

    execution = engine.execute_domains(
        ["PROCESS", "MEMORY", "NETWORK"]
    )

    assert set(execution["results"]) == {"PROCESS", "MEMORY"}
    assert set(execution["failures"]) == {"NETWORK"}
    assert "NETWORK" in engine.domain_failures
    assert engine.workflow.state == WorkflowState.INVESTIGATING


def test_7_20_partial_failure_can_still_aggregate():
    dispatcher = FakeDispatcher(
        results={
            "PROCESS": make_result(),
            "MEMORY": make_result(),
        },
        failures={
            "NETWORK": "network unavailable",
        },
    )

    engine = make_engine(dispatcher=dispatcher)

    engine.workflow.start_investigation()

    engine.execute_domains(
        ["PROCESS", "MEMORY", "NETWORK"]
    )

    result = engine.aggregate_domain_results()

    assert isinstance(result, WindowsDiagnosticResult)
    assert engine.domain_failures["NETWORK"]


# ============================================================
# 3. Full action lifecycle
# ============================================================

def prepare_action_engine():
    engine = make_engine()

    engine.workflow.start_investigation()
    engine.set_result(
        make_result([high_recommendation()])
    )
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True

    engine.prepare_remediation_authorization()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    action.operation = lambda: None

    engine.authorize_remediation(action_id)

    return engine, action_id


def test_7_20_full_action_path_reaches_verification():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    assert result.execution_status == "EXECUTED"
    assert engine.workflow.state == WorkflowState.VERIFYING
    assert engine.state == ProblemSolvingState.ACTION_REQUIRED


def test_7_20_full_action_path_reaches_resolution():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    verification = engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert verification["verified"] is True
    assert engine.workflow.state == WorkflowState.RESOLVED
    assert engine.state == ProblemSolvingState.RESOLVED


# ============================================================
# 4. Failed verification + recovery
# ============================================================

def test_7_20_failed_verification_enters_remediation_state():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    verification = engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="unhealthy",
    )

    assert verification["verified"] is False
    assert engine.workflow.state == WorkflowState.REMEDIATING
    assert engine.state == ProblemSolvingState.ACTION_REQUIRED


def test_7_20_recovery_creates_new_cycle_without_destroying_history():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="unhealthy",
    )

    original = engine.current_recovery_cycle

    recovery = engine.start_recovery_cycle()

    assert original.cycle_number == 0
    assert recovery.cycle_number == 1
    assert engine.recovery_cycle_count == 2
    assert engine.workflow.state == WorkflowState.INVESTIGATING


# ============================================================
# 5. Recovery diagnosis continuation
# ============================================================

def test_7_20_recovery_can_continue_into_new_diagnosis():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="unhealthy",
    )

    engine.start_recovery_cycle()

    engine.set_result(make_result())
    engine.workflow.mark_diagnosed()

    assert engine.workflow.state == WorkflowState.DIAGNOSED
    assert engine.recovery_cycle_count == 2


# ============================================================
# 6. Projection consistency
# ============================================================

@pytest.mark.parametrize(
    "workflow_transition",
    [
        "investigating",
        "diagnosed",
    ],
)
def test_7_20_projection_matches_workflow_during_diagnosis(
    workflow_transition,
):
    engine = make_engine()

    engine.workflow.start_investigation()

    if workflow_transition == "diagnosed":
        engine.set_result(make_result())
        engine.workflow.mark_diagnosed()

    projection = engine.projection()

    assert projection["workflow_state"] == engine.workflow.state
    assert projection["case_id"] == engine.case.case_id
    assert projection["recovery_cycle_count"] == 1


def test_7_20_projection_matches_resolved_lifecycle():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    projection = engine.projection()

    assert projection["workflow_state"] == WorkflowState.RESOLVED
    assert projection["verification_complete"] is True
    assert projection["verification_result"]["verified"] is True
    assert projection["execution_available"] is False


def test_7_20_projection_matches_recovery_lifecycle():
    engine, action_id = prepare_action_engine()

    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="unhealthy",
    )

    engine.start_recovery_cycle()

    projection = engine.projection()

    assert projection["workflow_state"] == WorkflowState.INVESTIGATING
    assert projection["recovery_cycle_count"] == 2
    assert len(projection["recovery_cycles"]) == 2
    assert projection["current_recovery_cycle"]["cycle_number"] == 1


# ============================================================
# 7. Integration safety
# ============================================================

def test_7_20_failed_domain_does_not_execute_remediation():
    dispatcher = FakeDispatcher(
        failures={"MEMORY": "memory diagnostic failed"}
    )

    engine = make_engine(dispatcher=dispatcher)

    engine.workflow.start_investigation()

    engine.execute_domains(["MEMORY"])

    assert engine.domain_failures["MEMORY"]
    assert engine.remediation_actions == {}


def test_7_20_projection_is_read_only_across_full_lifecycle():
    engine, action_id = prepare_action_engine()

    before = engine.workflow.history[:]

    projection = engine.projection()

    projection["lifecycle_history"].append(
        {"from": "CORRUPTED", "to": "CORRUPTED"}
    )

    assert engine.workflow.history == before


def test_7_20_complete_engine_surface_remains_available():
    engine = make_engine()

    assert hasattr(engine, "solve")
    assert hasattr(engine, "execute_domains")
    assert hasattr(engine, "aggregate_domain_results")
    assert hasattr(engine, "evaluate_action_requirement")
    assert hasattr(engine, "prepare_remediation_authorization")
    assert hasattr(engine, "authorize_remediation")
    assert hasattr(engine, "execute_remediation")
    assert hasattr(engine, "verify_remediation")
    assert hasattr(engine, "start_recovery_cycle")
    assert hasattr(engine, "projection")
