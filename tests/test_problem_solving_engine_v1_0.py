from engine.technician_verification import TechnicianVerification
from engine.remediation_result import RemediationResult
import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.problem_solving_engine import (
    ProblemSolvingState,
    ProductionProblemSolvingEngine,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.windows_diagnostic_investigation_coordinator import (
    WindowsDiagnosticInvestigationCoordinator,
)


class FakeDispatcher:
    def __init__(self):
        self.calls = []

    def dispatch(self, domain, evidence=None):
        self.calls.append((domain, evidence))
        return {
            "findings": [
                {
                    "finding": f"{domain}_PROBLEM",
                    "severity": "WARNING",
                }
            ]
        }


class FakeCoordinator:
    def __init__(self):
        self.calls = []

    def attach_result(self, case, result):
        self.calls.append((case, result))

        if isinstance(result, WindowsDiagnosticResult):
            case.set_findings(result.findings)
        else:
            case.set_findings(result.get("findings", []))

        return case


def make_engine(dispatcher=None, coordinator=None):
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return ProductionProblemSolvingEngine(
        case,
        workflow,
        registry,
        dispatcher=dispatcher,
        coordinator=coordinator,
    )


def test_requires_diagnostic_case():
    workflow = TechnicianWorkflow(DiagnosticCase())
    registry = WindowsDiagnosticEngineRegistry()

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            object(),
            workflow,
            registry,
        )


def test_requires_technician_workflow():
    case = DiagnosticCase()
    registry = WindowsDiagnosticEngineRegistry()

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case,
            object(),
            registry,
        )


def test_requires_canonical_diagnostic_registry():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case,
            workflow,
            object(),
        )


def test_workflow_must_reference_same_case():
    case = DiagnosticCase()
    other_case = DiagnosticCase()
    workflow = TechnicianWorkflow(other_case)
    registry = WindowsDiagnosticEngineRegistry()

    with pytest.raises(ValueError):
        ProductionProblemSolvingEngine(
            case,
            workflow,
            registry,
        )


def test_initial_state_is_pending():
    engine = make_engine()

    assert engine.state == ProblemSolvingState.PENDING
    assert engine.result is None
    assert engine.failure is None


def test_state_can_be_updated():
    engine = make_engine()

    assert engine.set_state(
        ProblemSolvingState.INVESTIGATING
    ) == ProblemSolvingState.INVESTIGATING


def test_invalid_state_is_rejected():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.set_state("NOT_A_REAL_STATE")


def test_result_is_defensive():
    engine = make_engine()

    engine.set_result(
        {
            "findings": [
                {"finding": "HIGH_MEMORY"}
            ]
        }
    )

    result = engine.result
    result["findings"].append(
        {"finding": "TAMPERED"}
    )

    assert len(engine.result["findings"]) == 1


def test_failure_records_error_and_changes_state():
    engine = make_engine()

    failure = engine.fail(
        RuntimeError("diagnostic failure")
    )

    assert failure == {
        "type": "RuntimeError",
        "message": "diagnostic failure",
    }
    assert engine.state == ProblemSolvingState.FAILED


def test_projection_exposes_canonical_case_identity():
    engine = make_engine()

    projection = engine.projection()

    assert projection["case_id"] == engine.case.case_id
    assert projection["machine_id"] is None
    assert projection["state"] == ProblemSolvingState.PENDING


def test_projection_is_defensive():
    engine = make_engine()

    engine.set_result(
        {
            "findings": [
                {"finding": "HIGH_MEMORY"}
            ]
        }
    )

    projection = engine.projection()
    projection["result"]["findings"].append(
        {"finding": "TAMPERED"}
    )

    assert len(engine.result["findings"]) == 1


def test_architecture_surface_reuses_canonical_components():
    engine = make_engine()

    surface = engine.architecture_surface()

    assert surface["case"] is engine.case
    assert surface["workflow"] is engine.workflow
    assert surface["diagnostic_registry"] is engine.diagnostic_registry


def test_engine_does_not_own_forbidden_processing_methods():
    engine = make_engine()

    forbidden = {
        "diagnose",
        "investigate",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert forbidden.isdisjoint(set(dir(engine)))


def test_dispatch_domain_uses_canonical_registry():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    result = engine.dispatch_domain("memory")

    assert result["findings"][0]["finding"] == "MEMORY_PROBLEM"
    assert dispatcher.calls == [("MEMORY", None)]
    assert engine.state == ProblemSolvingState.DIAGNOSED


def test_dispatch_domain_accepts_evidence():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    evidence = {"memory": {"used_percent": 90}}
    engine.dispatch_domain("MEMORY", evidence=evidence)

    assert dispatcher.calls == [("MEMORY", evidence)]


def test_dispatch_domain_rejects_unregistered_domain():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    with pytest.raises(ValueError):
        engine.dispatch_domain("UNKNOWN")

    assert dispatcher.calls == []


def test_attach_diagnostic_result_uses_canonical_coordinator():
    dispatcher = FakeDispatcher()
    coordinator = FakeCoordinator()
    engine = make_engine(
        dispatcher=dispatcher,
        coordinator=coordinator,
    )

    result = engine.dispatch_domain("MEMORY")
    case = engine.attach_diagnostic_result(result)

    assert case is engine.case
    assert case.findings == result["findings"]
    assert coordinator.calls[0][0] is engine.case


def test_attach_uses_stored_result_when_result_is_omitted():
    dispatcher = FakeDispatcher()
    coordinator = FakeCoordinator()
    engine = make_engine(
        dispatcher=dispatcher,
        coordinator=coordinator,
    )

    engine.dispatch_domain("MEMORY")
    engine.attach_diagnostic_result()

    assert engine.case.findings == [
        {
            "finding": "MEMORY_PROBLEM",
            "severity": "WARNING",
        }
    ]


def test_default_orchestration_components_are_canonical():
    engine = make_engine()

    assert isinstance(
        engine.dispatcher,
        WindowsDiagnosticDispatcher,
    )
    assert isinstance(
        engine.coordinator,
        WindowsDiagnosticInvestigationCoordinator,
    )


def test_dispatch_does_not_bypass_registry():
    class ExplodingDispatcher:
        def dispatch(self, domain, evidence=None):
            raise AssertionError("dispatcher must not be called")

    engine = make_engine(dispatcher=ExplodingDispatcher())

    with pytest.raises(ValueError):
        engine.dispatch_domain("NOT_SUPPORTED")


def test_diagnostic_result_is_stored_defensively():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    result = engine.dispatch_domain("MEMORY")
    result["findings"].append({"finding": "TAMPERED"})

    assert len(engine.result["findings"]) == 1


def test_execute_domains_runs_all_registered_domains():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    summary = engine.execute_domains(
        ["PROCESS", "MEMORY", "SYSTEM"]
    )

    assert dispatcher.calls == [
        ("PROCESS", None),
        ("MEMORY", None),
        ("SYSTEM", None),
    ]
    assert set(summary["results"]) == {
        "PROCESS",
        "MEMORY",
        "SYSTEM",
    }
    assert summary["failures"] == {}
    assert engine.state == ProblemSolvingState.DIAGNOSED


def test_execute_domains_isolates_domain_failure():
    class SelectiveDispatcher:
        def __init__(self):
            self.calls = []

        def dispatch(self, domain, evidence=None):
            self.calls.append(domain)

            if domain == "NETWORK":
                raise RuntimeError("network diagnostic unavailable")

            return {
                "findings": [
                    {
                        "finding": f"{domain}_PROBLEM",
                        "severity": "WARNING",
                    }
                ]
            }

    dispatcher = SelectiveDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    summary = engine.execute_domains(
        ["PROCESS", "NETWORK", "SYSTEM"]
    )

    assert dispatcher.calls == [
        "PROCESS",
        "NETWORK",
        "SYSTEM",
    ]

    assert set(summary["results"]) == {
        "PROCESS",
        "SYSTEM",
    }

    assert summary["failures"]["NETWORK"] == {
        "type": "RuntimeError",
        "message": "network diagnostic unavailable",
    }

    assert engine.state == ProblemSolvingState.DIAGNOSED


def test_execute_domains_all_failures_transition_to_failed():
    class FailingDispatcher:
        def dispatch(self, domain, evidence=None):
            raise RuntimeError(
                f"{domain} diagnostic failed"
            )

    engine = make_engine(
        dispatcher=FailingDispatcher()
    )

    summary = engine.execute_domains(
        ["MEMORY", "NETWORK"]
    )

    assert summary["results"] == {}
    assert set(summary["failures"]) == {
        "MEMORY",
        "NETWORK",
    }
    assert engine.state == ProblemSolvingState.FAILED


def test_execute_domains_deduplicates_domains():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    engine.execute_domains(
        ["MEMORY", "memory", " MEMORY "]
    )

    assert dispatcher.calls == [
        ("MEMORY", None),
    ]


def test_execute_domains_rejects_unregistered_domain_before_execution():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    with pytest.raises(ValueError):
        engine.execute_domains(
            ["MEMORY", "UNKNOWN", "SYSTEM"]
        )

    assert dispatcher.calls == []


def test_execute_domains_preserves_evidence_for_each_domain():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    evidence = {
        "memory": {
            "used_percent": 91,
        }
    }

    engine.execute_domains(
        ["MEMORY", "SYSTEM"],
        evidence=evidence,
    )

    assert dispatcher.calls == [
        ("MEMORY", evidence),
        ("SYSTEM", evidence),
    ]


def test_domain_results_are_defensively_returned():
    dispatcher = FakeDispatcher()
    engine = make_engine(dispatcher=dispatcher)

    engine.execute_domains(["MEMORY"])

    results = engine.domain_results
    results["MEMORY"]["findings"].append(
        {"finding": "TAMPERED"}
    )

    assert len(
        engine.domain_results["MEMORY"]["findings"]
    ) == 1


def test_domain_failures_are_defensively_returned():
    class FailingDispatcher:
        def dispatch(self, domain, evidence=None):
            raise RuntimeError("diagnostic failed")

    engine = make_engine(
        dispatcher=FailingDispatcher()
    )

    engine.execute_domains(["MEMORY"])

    failures = engine.domain_failures
    failures["MEMORY"]["message"] = "TAMPERED"

    assert (
        engine.domain_failures["MEMORY"]["message"]
        == "diagnostic failed"
    )


def test_aggregate_domain_results_returns_canonical_result():
    class RichDispatcher:
        def dispatch(self, domain, evidence=None):
            return WindowsDiagnosticResult(
                observations=[f"{domain}_OBS"],
                signals=[f"{domain}_SIGNAL"],
                findings=[f"{domain}_FINDING"],
                correlations=[f"{domain}_CORRELATION"],
                candidates=[f"{domain}_CANDIDATE"],
                primary_cause=(
                    f"{domain}_CAUSE"
                    if domain == "MEMORY"
                    else None
                ),
                recommendations=[f"{domain}_RECOMMENDATION"],
                confidences=[f"{domain}_CONFIDENCE"],
            )

    engine = make_engine(
        dispatcher=RichDispatcher()
    )

    engine.execute_domains(
        ["PROCESS", "MEMORY"]
    )

    result = engine.aggregate_domain_results()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert result.observations == [
        "PROCESS_OBS",
        "MEMORY_OBS",
    ]

    assert result.signals == [
        "PROCESS_SIGNAL",
        "MEMORY_SIGNAL",
    ]

    assert result.findings == [
        "PROCESS_FINDING",
        "MEMORY_FINDING",
    ]

    assert result.correlations == [
        "PROCESS_CORRELATION",
        "MEMORY_CORRELATION",
    ]

    assert result.candidates == [
        "PROCESS_CANDIDATE",
        "MEMORY_CANDIDATE",
    ]

    assert result.primary_cause == "MEMORY_CAUSE"

    assert result.recommendations == [
        "PROCESS_RECOMMENDATION",
        "MEMORY_RECOMMENDATION",
    ]

    assert result.confidences == [
        "PROCESS_CONFIDENCE",
        "MEMORY_CONFIDENCE",
    ]


def test_aggregate_domain_results_normalizes_dictionary_results():
    dispatcher = FakeDispatcher()
    engine = make_engine(
        dispatcher=dispatcher
    )

    engine.execute_domains(
        ["MEMORY", "SYSTEM"]
    )

    result = engine.aggregate_domain_results()

    assert isinstance(
        result,
        WindowsDiagnosticResult,
    )

    assert len(result.findings) == 2


def test_aggregate_domain_results_preserves_domain_failures():
    class SelectiveDispatcher:
        def dispatch(self, domain, evidence=None):
            if domain == "NETWORK":
                raise RuntimeError(
                    "network unavailable"
                )

            return {
                "findings": [
                    f"{domain}_FINDING"
                ]
            }

    engine = make_engine(
        dispatcher=SelectiveDispatcher()
    )

    engine.execute_domains(
        ["MEMORY", "NETWORK", "SYSTEM"]
    )

    result = engine.aggregate_domain_results()

    assert result.findings == [
        "MEMORY_FINDING",
        "SYSTEM_FINDING",
    ]

    assert engine.domain_failures["NETWORK"][
        "type"
    ] == "RuntimeError"


def test_aggregate_domain_results_updates_engine_result():
    dispatcher = FakeDispatcher()
    engine = make_engine(
        dispatcher=dispatcher
    )

    engine.execute_domains(
        ["MEMORY", "SYSTEM"]
    )

    aggregated = engine.aggregate_domain_results()

    assert isinstance(
        engine.result,
        WindowsDiagnosticResult,
    )

    assert engine.result.findings == (
        aggregated.findings
    )

    assert engine.state == (
        ProblemSolvingState.DIAGNOSED
    )


def test_aggregate_domain_results_does_not_attach_case():
    dispatcher = FakeDispatcher()
    engine = make_engine(
        dispatcher=dispatcher
    )

    engine.execute_domains(["MEMORY"])

    engine.aggregate_domain_results()

    assert engine.case.findings == []


def test_aggregate_domain_results_requires_successful_results():
    engine = make_engine()

    with pytest.raises(ValueError):
        engine.aggregate_domain_results()


def test_aggregate_preserves_canonical_object_identity():
    observation = object()
    signal = object()
    finding = object()

    result = WindowsDiagnosticResult(
        observations=[observation],
        signals=[signal],
        findings=[finding],
    )

    class CanonicalDispatcher:
        def dispatch(self, domain, evidence=None):
            return result

    engine = make_engine(
        dispatcher=CanonicalDispatcher()
    )

    engine.execute_domains(["MEMORY"])

    aggregated = engine.aggregate_domain_results()

    assert aggregated.observations[0] is observation
    assert aggregated.signals[0] is signal
    assert aggregated.findings[0] is finding


def test_aggregate_primary_cause_uses_first_available_cause():
    class CauseDispatcher:
        def dispatch(self, domain, evidence=None):
            return WindowsDiagnosticResult(
                primary_cause=(
                    "PROCESS_CAUSE"
                    if domain == "PROCESS"
                    else "MEMORY_CAUSE"
                )
            )

    engine = make_engine(
        dispatcher=CauseDispatcher()
    )

    engine.execute_domains(
        ["PROCESS", "MEMORY"]
    )

    aggregated = (
        engine.aggregate_domain_results()
    )

    assert (
        aggregated.primary_cause
        == "PROCESS_CAUSE"
    )


def test_solve_composes_execution_aggregation_and_case_attachment():
    dispatcher = FakeDispatcher()
    coordinator = FakeCoordinator()

    engine = make_engine(
        dispatcher=dispatcher,
        coordinator=coordinator,
    )

    summary = engine.solve(
        ["MEMORY", "SYSTEM"]
    )

    assert summary["state"] == (
        ProblemSolvingState.DIAGNOSED
    )

    assert isinstance(
        summary["result"],
        WindowsDiagnosticResult,
    )

    assert summary["case"] is engine.case

    assert summary["case"].findings == [
        {
            "finding": "MEMORY_PROBLEM",
            "severity": "WARNING",
        },
        {
            "finding": "SYSTEM_PROBLEM",
            "severity": "WARNING",
        },
    ]

    assert len(coordinator.calls) == 1


def test_solve_preserves_partial_success():
    class SelectiveDispatcher:
        def dispatch(self, domain, evidence=None):
            if domain == "NETWORK":
                raise RuntimeError(
                    "network unavailable"
                )

            return {
                "findings": [
                    f"{domain}_FINDING"
                ]
            }

    engine = make_engine(
        dispatcher=SelectiveDispatcher()
    )

    summary = engine.solve(
        ["MEMORY", "NETWORK", "SYSTEM"]
    )

    assert summary["state"] == (
        ProblemSolvingState.DIAGNOSED
    )

    assert summary["result"].findings == [
        "MEMORY_FINDING",
        "SYSTEM_FINDING",
    ]

    assert summary["domain_failures"][
        "NETWORK"
    ]["type"] == "RuntimeError"

    assert engine.case.findings == [
        "MEMORY_FINDING",
        "SYSTEM_FINDING",
    ]


def test_solve_all_failures_do_not_attach_result():
    class FailingDispatcher:
        def dispatch(self, domain, evidence=None):
            raise RuntimeError(
                f"{domain} failed"
            )

    coordinator = FakeCoordinator()

    engine = make_engine(
        dispatcher=FailingDispatcher(),
        coordinator=coordinator,
    )

    summary = engine.solve(
        ["MEMORY", "NETWORK"]
    )

    assert summary["state"] == (
        ProblemSolvingState.FAILED
    )

    assert summary["result"] is None
    assert summary["domain_results"] == {}
    assert set(summary["domain_failures"]) == {
        "MEMORY",
        "NETWORK",
    }

    assert coordinator.calls == []
    assert engine.case.findings == []


def test_solve_passes_evidence_through_entire_execution():
    dispatcher = FakeDispatcher()

    engine = make_engine(
        dispatcher=dispatcher
    )

    evidence = {
        "memory": {
            "used_percent": 92
        }
    }

    summary = engine.solve(
        ["MEMORY", "SYSTEM"],
        evidence=evidence,
    )

    assert summary["state"] == (
        ProblemSolvingState.DIAGNOSED
    )

    assert dispatcher.calls == [
        ("MEMORY", evidence),
        ("SYSTEM", evidence),
    ]


def test_solve_returns_canonical_case_and_result():
    dispatcher = FakeDispatcher()
    coordinator = FakeCoordinator()

    engine = make_engine(
        dispatcher=dispatcher,
        coordinator=coordinator,
    )

    summary = engine.solve(["MEMORY"])

    assert summary["case"] is engine.case
    assert isinstance(
        summary["result"],
        WindowsDiagnosticResult,
    )

    assert coordinator.calls[0][0] is engine.case
    assert coordinator.calls[0][1] is summary["result"]


def test_solve_does_not_create_duplicate_dispatcher():
    dispatcher = FakeDispatcher()

    engine = make_engine(
        dispatcher=dispatcher
    )

    engine.solve(["MEMORY"])

    assert engine.dispatcher is dispatcher


def test_solve_does_not_create_duplicate_coordinator():
    coordinator = FakeCoordinator()

    engine = make_engine(
        coordinator=coordinator
    )

    engine.solve(["MEMORY"])

    assert engine.coordinator is coordinator


def test_solve_projection_reflects_completed_case_integration():
    engine = make_engine()

    engine.solve(["MEMORY"])

    projection = engine.projection()

    assert projection["state"] == (
        ProblemSolvingState.DIAGNOSED
    )

    assert projection["result"] is not None
    assert projection["domain_results"]
    assert projection["domain_failures"] == {}

def _make_recommendation(priority="HIGH"):
    from engine.recommendation import Recommendation

    return Recommendation(
        recommendation_type="memory_review",
        category="MEMORY",
        priority=priority,
        description="Review excessive memory consumption.",
        rationale="Memory pressure exceeds the configured threshold.",
    )


def _make_result_with_recommendations(recommendations):
    from engine.windows_diagnostic_result import (
        WindowsDiagnosticResult,
    )

    return WindowsDiagnosticResult(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        primary_cause=None,
        recommendations=recommendations,
        confidences=[],
    )


def test_solve_marks_action_required_for_eligible_recommendation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.dispatch_domain = lambda domain, evidence=None: (
        _make_result_with_recommendations([recommendation])
    )

    result = engine.solve(["MEMORY"])

    assert result["action_required"] is True
    assert result["state"] == ProblemSolvingState.ACTION_REQUIRED
    assert (
        result["workflow_state"]
        is WorkflowState.ACTION_REQUIRED
    )


def test_solve_keeps_diagnosed_for_ineligible_recommendation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("MEDIUM")

    engine.dispatch_domain = lambda domain, evidence=None: (
        _make_result_with_recommendations([recommendation])
    )

    result = engine.solve(["MEMORY"])

    assert result["action_required"] is False
    assert result["state"] == ProblemSolvingState.DIAGNOSED
    assert result["workflow_state"] is WorkflowState.DIAGNOSED


def test_solve_keeps_diagnosed_without_recommendations():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    engine.dispatch_domain = lambda domain, evidence=None: (
        _make_result_with_recommendations([])
    )

    result = engine.solve(["MEMORY"])

    assert result["action_required"] is False
    assert result["state"] == ProblemSolvingState.DIAGNOSED
    assert result["workflow_state"] is WorkflowState.DIAGNOSED


def test_action_decision_uses_canonical_remediation_boundary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("CRITICAL")

    engine._result = _make_result_with_recommendations(
        [recommendation]
    )
    workflow.start_investigation()
    workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True
    assert len(decision["decisions"]) == 1
    assert decision["decisions"][0].eligible is True


def test_action_decision_does_not_authorize_remediation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine._result = _make_result_with_recommendations(
        [recommendation]
    )
    workflow.start_investigation()
    workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True

    # Phase 7.8 provides an explicit authorization boundary.
    # Evaluation alone must not authorize the remediation action.
    prepared = engine.prepare_remediation_authorization()

    assert len(prepared["actions"]) == 1
    assert len(prepared["authorizations"]) == 1

    action_id = next(iter(prepared["authorizations"]))

    authorization = engine.authorization_for(action_id)

    assert authorization.state.value == "UNAUTHORIZED"
    assert authorization.reason.value == "NOT_REQUESTED"
    assert engine.authorization_allows_execution(action_id) is False

def test_action_decision_does_not_execute_remediation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine._result = _make_result_with_recommendations(
        [recommendation]
    )
    workflow.start_investigation()
    workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True
    assert hasattr(engine, "execute_remediation")

    # Evaluation identifies the need for remediation.
    # It must not execute or automatically prepare an action.
    assert engine.remediation_actions == {}
    assert engine.authorizations == {}

def test_solve_preserves_canonical_case_and_workflow_identity():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.dispatch_domain = lambda domain, evidence=None: (
        _make_result_with_recommendations([recommendation])
    )

    result = engine.solve(["MEMORY"])

    assert result["case"] is case
    assert engine.case is case
    assert engine.workflow is workflow
    assert workflow.case is case


def test_projection_exposes_action_required_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.dispatch_domain = lambda domain, evidence=None: (
        _make_result_with_recommendations([recommendation])
    )

    engine.solve(["MEMORY"])

    projection = engine.projection()
    assert (
        projection["workflow_state"]
        is WorkflowState.ACTION_REQUIRED
    )
    assert projection["action_required"] is True






# ============================================================
# Phase 7.8 â€” Authorization Boundary Integration
# ============================================================

from packaging.remediation_authorization import (
    AuthorizationReason,
    AuthorizationState,
    RemediationAuthorization,
)


def test_solve_prepares_unauthorized_remediation_for_eligible_recommendation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    result = engine.evaluate_action_requirement()

    assert result["action_required"] is True

    prepared = (
        engine.prepare_remediation_authorization()
    )

    assert prepared["actions"]
    assert prepared["authorizations"]

    for action_id, authorization in (
        prepared["authorizations"].items()
    ):
        assert isinstance(
            authorization,
            RemediationAuthorization,
        )
        assert authorization.action_id == action_id
        assert (
            authorization.state
            is AuthorizationState.UNAUTHORIZED
        )
        assert (
            authorization.reason
            is AuthorizationReason.NOT_REQUESTED
        )
        assert (
            prepared["actions"][action_id].execution_status
            == "NOT_EXECUTED"
        )


def test_prepared_authorization_does_not_execute_action():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    for action in prepared["actions"].values():
        assert action.execution_status == "NOT_EXECUTED"


def test_authorization_is_not_granted_automatically():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    for authorization in (
        prepared["authorizations"].values()
    ):
        assert (
            authorization.state
            is AuthorizationState.UNAUTHORIZED
        )


def test_explicit_user_authorization_changes_only_authorization_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    action_id = next(
        iter(prepared["actions"])
    )

    authorization = (
        engine.authorize_remediation(action_id)
    )

    assert authorization.state is (
        AuthorizationState.AUTHORIZED
    )
    assert authorization.reason is (
        AuthorizationReason.USER_APPROVED
    )

    assert (
        engine.remediation_actions[action_id]
        .execution_status
        == "NOT_EXECUTED"
    )

    assert workflow.state is WorkflowState.DIAGNOSED


def test_explicit_technician_authorization_uses_technician_reason():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="CRITICAL"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    action_id = next(
        iter(prepared["actions"])
    )

    authorization = (
        engine.authorize_remediation(
            action_id,
            technician=True,
        )
    )

    assert authorization.state is (
        AuthorizationState.AUTHORIZED
    )
    assert authorization.reason is (
        AuthorizationReason.TECHNICIAN_APPROVED
    )


def test_explicit_denial_blocks_execution():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    action_id = next(
        iter(prepared["actions"])
    )

    authorization = (
        engine.deny_remediation(action_id)
    )

    assert authorization.state is (
        AuthorizationState.DENIED
    )
    assert authorization.reason is (
        AuthorizationReason.USER_DENIED
    )
    assert (
        engine.authorization_allows_execution(
            action_id
        )
        is False
    )


def test_medium_recommendation_does_not_create_authorization():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="MEDIUM"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    result = engine.evaluate_action_requirement()

    assert result["action_required"] is False

    prepared = (
        engine.prepare_remediation_authorization()
    )

    assert prepared["actions"] == {}
    assert prepared["authorizations"] == {}


def test_authorization_does_not_bind_or_create_operation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    prepared = (
        engine.prepare_remediation_authorization()
    )

    action_id = next(
        iter(prepared["actions"])
    )

    engine.authorize_remediation(action_id)

    action = engine.remediation_actions[action_id]

    assert action.operation is None
    assert action.execution_status == "NOT_EXECUTED"


def test_projection_exposes_authorization_boundary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    engine.evaluate_action_requirement()
    engine.prepare_remediation_authorization()

    projection = engine.projection()

    assert projection["remediation_actions"]
    assert projection["authorizations"]

    for authorization in projection[
        "authorizations"
    ].values():
        assert isinstance(
            authorization,
            RemediationAuthorization,
        )
        assert authorization.state is (
            AuthorizationState.UNAUTHORIZED
        )


def test_authorization_records_are_defensive():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation(
        priority="HIGH"
    )

    engine.set_result(
        {
            "recommendations": [recommendation],
        }
    )

    engine._state = ProblemSolvingState.DIAGNOSED
    workflow.state = WorkflowState.DIAGNOSED

    engine.evaluate_action_requirement()
    engine.prepare_remediation_authorization()

    authorizations = engine.authorizations

    action_id = next(iter(authorizations))

    assert (
        authorizations[action_id]
        is not engine.authorizations[action_id]
    )

# ============================================================
# PHASE 7.9 â€” EXECUTION BOUNDARY
# ============================================================

def test_7_9_unauthorized_remediation_cannot_execute():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED
    engine._state = ProblemSolvingState.ACTION_REQUIRED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    with pytest.raises(PermissionError):
        engine.execute_remediation(action_id)

    assert action.execution_status == "NOT_EXECUTED"


def test_7_9_denied_remediation_cannot_execute():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("CRITICAL")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.deny_remediation(action_id)

    with pytest.raises(PermissionError):
        engine.execute_remediation(action_id)

    assert action.execution_status == "NOT_EXECUTED"


def test_7_9_authorized_action_without_operation_cannot_execute():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    engine.authorize_remediation(action_id)

    with pytest.raises(ValueError, match="no bound operation"):
        engine.execute_remediation(action_id)


def test_7_9_authorized_bound_action_executes_through_coordinator():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]

    calls = []

    def operation():
        calls.append("executed")

    action.operation = operation

    authorization = engine.authorize_remediation(action_id)

    assert authorization.state.value == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    result = engine.execute_remediation(action_id)

    assert calls == ["executed"]
    assert result.action_id == action_id
    assert result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING


def test_7_9_execution_does_not_bind_operation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]
    assert action.operation is None

    engine.authorize_remediation(action_id)

    with pytest.raises(ValueError, match="no bound operation"):
        engine.execute_remediation(action_id)

    assert action.operation is None


def test_7_9_execution_requires_explicit_authorization():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    assert engine.authorization_allows_execution(action_id) is False

    with pytest.raises(PermissionError):
        engine.execute_remediation(action_id)

    assert action.execution_status == "NOT_EXECUTED"


def test_7_9_successful_execution_enters_verification():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("CRITICAL")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(
        action_id,
        technician=True,
    )

    result = engine.execute_remediation(action_id)

    assert result.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING


def test_7_9_projection_reports_execution_availability():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )
    workflow.state = WorkflowState.DIAGNOSED

    prepared = engine.prepare_remediation_authorization()
    action_id = next(iter(prepared["actions"]))

    projection = engine.projection()

    assert projection["execution_available"] is False

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)

    projection = engine.projection()

    assert projection["execution_available"] is True

# ============================================================
# PHASE 7.10 â€” VERIFICATION & RESOLUTION INTEGRATION
# ============================================================

def test_7_10_engine_owns_canonical_technician_verification():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    assert isinstance(
        engine.verification,
        TechnicianVerification,
    )


def test_7_10_successful_verification_resolves_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-success")
    action.execution_status = "EXECUTED"

    result = engine.verify_remediation(
        result=action,
        expected={"status": "NORMAL"},
        observed={"status": "NORMAL"},
    )

    assert result["verified"] is True
    assert workflow.state is WorkflowState.RESOLVED
    assert engine.verification_complete is True
    assert result["verification_result"]["verified"] is True
    assert engine.state is ProblemSolvingState.RESOLVED


def test_7_10_failed_verification_returns_to_remediating():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-failure")
    action.execution_status = "EXECUTED"

    result = engine.verify_remediation(
        result=action,
        expected={"status": "NORMAL"},
        observed={"status": "WARNING"},
    )

    assert result["verified"] is False
    assert workflow.state is WorkflowState.REMEDIATING
    assert engine.verification_complete is False
    assert result["verification_result"]["verified"] is False
    assert engine.state is ProblemSolvingState.ACTION_REQUIRED


def test_7_10_verification_preserves_canonical_verification_data():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-data")
    action.execution_status = "EXECUTED"

    engine.verify_remediation(
        result=action,
        expected="healthy",
        observed="healthy",
    )

    verification = engine.verification_result

    assert verification["action_id"] == "action-7-10-data"
    assert verification["expected"] == "healthy"
    assert verification["observed"] == "healthy"
    assert verification["verified"] is True


def test_7_10_verification_requires_executed_remediation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-invalid")

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=action,
            expected="healthy",
            observed="healthy",
        )


def test_7_10_verification_requires_expected_condition():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-expected")
    action.execution_status = "EXECUTED"

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=action,
            expected=None,
            observed="healthy",
        )


def test_7_10_verification_requires_observed_condition():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-observed")
    action.execution_status = "EXECUTED"

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=action,
            expected="healthy",
            observed=None,
        )


def test_7_10_verification_cannot_start_outside_verifying_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    action = RemediationResult("action-7-10-state")
    action.execution_status = "EXECUTED"

    with pytest.raises(ValueError):
        engine.verify_remediation(
            result=action,
            expected="healthy",
            observed="healthy",
        )


def test_7_10_projection_exposes_verification_boundary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    projection = engine.projection()

    assert "verification_result" in projection
    assert "verification_complete" in projection
    assert projection["verification_result"] is None
    assert projection["verification_complete"] is False


def test_7_10_successful_verification_updates_projection():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    action = RemediationResult("action-7-10-projection")
    action.execution_status = "EXECUTED"

    engine.verify_remediation(
        result=action,
        expected="healthy",
        observed="healthy",
    )

    projection = engine.projection()

    assert projection["verification_complete"] is True
    assert projection["verification_result"]["verified"] is True
    assert projection["workflow_state"] is WorkflowState.RESOLVED
    assert projection["state"] is ProblemSolvingState.RESOLVED
# ============================================================================
# PHASE 7.10 â€” VERIFICATION & RESOLUTION INTEGRATION
# ============================================================================

def test_engine_owns_canonical_technician_verification():
    engine = make_engine()

    assert isinstance(engine.verification, TechnicianVerification)
    assert engine.verification.workflow is engine.workflow


def test_verification_projection_is_exposed():
    engine = make_engine()

    projection = engine.projection()

    assert "verification_result" in projection
    assert "verification_complete" in projection
    assert projection["verification_result"] is None
    assert projection["verification_complete"] is False


def test_7_10_engine_owns_canonical_technician_verification():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    assert isinstance(engine.verification, TechnicianVerification)
    assert engine.verification.workflow is workflow


def test_7_10_successful_verification_resolves_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-success")
    result.execution_status = "EXECUTED"

    verification = engine.verify_remediation(
        result=result,
        expected={"healthy": True},
        observed={"healthy": True},
    )

    assert verification["verified"] is True
    assert workflow.state is WorkflowState.RESOLVED
    assert engine.state is ProblemSolvingState.RESOLVED
    assert engine.verification_complete is True


def test_7_10_failed_verification_returns_to_remediating():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-failure")
    result.execution_status = "EXECUTED"

    verification = engine.verify_remediation(
        result=result,
        expected={"healthy": True},
        observed={"healthy": False},
    )

    assert verification["verified"] is False
    assert workflow.state is WorkflowState.REMEDIATING


def test_7_10_verification_preserves_result_data():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-data")
    result.execution_status = "EXECUTED"

    engine.verify_remediation(
        result=result,
        expected={"healthy": True},
        observed={"healthy": True},
    )

    verification = engine.verification_result

    assert verification["action_id"] == "action-7-10-data"
    assert verification["verified"] is True
    assert verification["expected"] == {"healthy": True}
    assert verification["observed"] == {"healthy": True}


def test_7_10_requires_executed_remediation():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-invalid")

    with pytest.raises(ValueError, match="successfully executed"):
        engine.verify_remediation(
            result=result,
            expected={"healthy": True},
            observed={"healthy": True},
        )


def test_7_10_requires_expected_condition():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-expected")
    result.execution_status = "EXECUTED"

    with pytest.raises(ValueError, match="Expected condition"):
        engine.verify_remediation(
            result=result,
            observed={"healthy": True},
        )


def test_7_10_requires_observed_condition():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-observed")
    result.execution_status = "EXECUTED"

    with pytest.raises(ValueError, match="Observed condition"):
        engine.verify_remediation(
            result=result,
            expected={"healthy": True},
        )


def test_7_10_requires_verifying_workflow_state():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    result = RemediationResult("action-7-10-state")
    result.execution_status = "EXECUTED"

    with pytest.raises(ValueError, match="VERIFYING"):
        engine.verify_remediation(
            result=result,
            expected={"healthy": True},
            observed={"healthy": True},
        )


def test_7_10_projection_exposes_verification_boundary():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    projection = engine.projection()

    assert "verification_result" in projection
    assert "verification_complete" in projection
    assert projection["verification_result"] is None
    assert projection["verification_complete"] is False


def test_7_10_successful_verification_updates_projection():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    engine = ProductionProblemSolvingEngine(
        case=case,
        workflow=workflow,
        diagnostic_registry=WindowsDiagnosticEngineRegistry(),
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    result = RemediationResult("action-7-10-projection")
    result.execution_status = "EXECUTED"

    engine.verify_remediation(
        result=result,
        expected={"healthy": True},
        observed={"healthy": True},
    )

    projection = engine.projection()

    assert projection["verification_result"]["verified"] is True
    assert projection["verification_complete"] is True
    assert projection["workflow_state"] is WorkflowState.RESOLVED
from engine.problem_solving_engine import (
    ProblemSolvingState,
    ProductionProblemSolvingEngine,
)
from engine.technician_workflow import WorkflowState
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow
from engine.windows_diagnostic_engine_registry import WindowsDiagnosticEngineRegistry


def make_recovery_engine():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    registry = WindowsDiagnosticEngineRegistry()

    return ProductionProblemSolvingEngine(
        case,
        workflow,
        registry,
    )


def test_7_11_engine_starts_with_original_recovery_cycle():
    engine = make_recovery_engine()

    assert engine.recovery_cycle_count == 1
    assert len(engine.recovery_cycles) == 1
    assert engine.current_recovery_cycle.cycle_number == 0
    assert engine.current_recovery_cycle.is_original is True
    assert engine.current_recovery_cycle.is_recovery is False
    assert engine.current_recovery_cycle.workflow is engine.workflow


def test_7_11_failed_verification_does_not_create_recovery_cycle():
    engine = make_recovery_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()
    engine.workflow.start_verification()

    assert engine.recovery_cycle_count == 1
    assert engine.current_recovery_cycle.cycle_number == 0


def test_7_11_explicit_recovery_creates_cycle_one():
    engine = make_recovery_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    cycle = engine.start_recovery_cycle()

    assert cycle.cycle_number == 1
    assert cycle.is_recovery is True
    assert cycle.workflow is engine.workflow
    assert engine.workflow.state is WorkflowState.INVESTIGATING
    assert engine.recovery_cycle_count == 2


def test_7_11_recovery_preserves_original_cycle():
    engine = make_recovery_engine()

    original = engine.current_recovery_cycle

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    engine.start_recovery_cycle()

    assert engine.recovery_cycles[0] is original
    assert engine.recovery_cycles[0].cycle_number == 0
    assert engine.recovery_cycles[1].cycle_number == 1


def test_7_11_recovery_does_not_execute_remediation():
    engine = make_recovery_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    assert engine.last_remediation_result is None

    engine.start_recovery_cycle()

    assert engine.last_remediation_result is None
    assert engine.workflow.state is WorkflowState.INVESTIGATING


def test_7_11_recovery_can_create_cycle_two():
    engine = make_recovery_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    first = engine.start_recovery_cycle()

    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    second = engine.start_recovery_cycle()

    assert first.cycle_number == 1
    assert second.cycle_number == 2
    assert engine.recovery_cycle_count == 3
    assert [c.cycle_number for c in engine.recovery_cycles] == [0, 1, 2]


def test_7_11_recovery_requires_remediating_workflow():
    engine = make_recovery_engine()

    try:
        engine.start_recovery_cycle()
    except ValueError as exc:
        assert "REMEDIATING" in str(exc)
    else:
        raise AssertionError(
            "Recovery should require the REMEDIATING workflow state."
        )


def test_7_11_recovery_projection_is_defensive():
    engine = make_recovery_engine()

    projection = engine.projection()

    projection["recovery_cycles"].append(
        {"cycle_number": 999}
    )

    assert engine.recovery_cycle_count == 1
    assert len(engine.recovery_cycles) == 1


def test_7_11_recovery_projection_exposes_current_cycle():
    engine = make_recovery_engine()

    projection = engine.projection()

    assert projection["recovery_cycle_count"] == 1
    assert projection["current_recovery_cycle"]["cycle_number"] == 0
    assert projection["current_recovery_cycle"]["is_original"] is True
    assert projection["current_recovery_cycle"]["is_recovery"] is False


def test_7_11_recovery_is_explicit_not_automatic():
    engine = make_recovery_engine()

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()
    engine.workflow.require_action()
    engine.workflow.start_remediation()

    assert engine.recovery_cycle_count == 1

    # No recovery cycle is created merely because remediation exists.
    assert engine.current_recovery_cycle.cycle_number == 0
from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.technician_workflow import WorkflowState
from engine.remediation_result import RemediationResult


# ============================================================
# PHASE 7.12 — PRODUCTION CASE LIFECYCLE INTEGRATION
# ============================================================

def _make_7_12_eligible_engine():
    engine = make_engine()

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    decision = engine.evaluate_action_requirement()

    assert decision["action_required"] is True

    prepared = engine.prepare_remediation_authorization()

    assert prepared["actions"]

    return engine


def test_7_12_successful_production_lifecycle():
    engine = _make_7_12_eligible_engine()

    assert engine.workflow.state is WorkflowState.ACTION_REQUIRED
    assert engine.state is ProblemSolvingState.ACTION_REQUIRED

    action_id = next(iter(engine.remediation_actions))

    authorization = engine.authorize_remediation(action_id)

    assert authorization.action_id == action_id
    assert engine.authorization_allows_execution(action_id) is True

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    remediation_result = engine.execute_remediation(action_id)

    assert isinstance(remediation_result, RemediationResult)
    assert remediation_result.execution_status == "EXECUTED"
    assert engine.workflow.state is WorkflowState.VERIFYING

    verification = engine.verify_remediation(
        result=remediation_result,
        expected={"status": "healthy"},
        observed={"status": "healthy"},
    )

    assert verification["verified"] is True
    assert verification["workflow_state"] is WorkflowState.RESOLVED
    assert engine.workflow.state is WorkflowState.RESOLVED
    assert engine.state is ProblemSolvingState.RESOLVED
    assert engine.verification_complete is True


def test_7_12_failed_verification_enters_explicit_recovery_path():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    engine.authorize_remediation(action_id)

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    remediation_result = engine.execute_remediation(action_id)

    assert remediation_result.execution_status == "EXECUTED"
    assert engine.workflow.state is WorkflowState.VERIFYING

    verification = engine.verify_remediation(
        result=remediation_result,
        expected={"status": "healthy"},
        observed={"status": "still_unhealthy"},
    )

    assert verification["verified"] is False
    assert engine.workflow.state is WorkflowState.REMEDIATING

    # Verification failure does not silently create a recovery cycle.
    assert engine.recovery_cycle_count == 1

    recovery_cycle = engine.start_recovery_cycle()

    assert recovery_cycle.cycle_number == 1
    assert recovery_cycle.is_recovery is True
    assert engine.workflow.state is WorkflowState.INVESTIGATING
    assert engine.recovery_cycle_count == 2


def test_7_12_authorization_is_required_before_execution():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    assert engine.authorization_allows_execution(action_id) is False

    with pytest.raises(PermissionError):
        engine.execute_remediation(action_id)


def test_7_12_execution_enters_verification():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)

    result = engine.execute_remediation(action_id)

    assert result.execution_status == "EXECUTED"
    assert engine.workflow.state is WorkflowState.VERIFYING
    assert engine.verification_complete is False


def test_7_12_successful_verification_resolves_case():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    verification = engine.verify_remediation(
        result=result,
        expected={"status": "healthy"},
        observed={"status": "healthy"},
    )

    assert verification["verified"] is True
    assert engine.workflow.state is WorkflowState.RESOLVED
    assert engine.state is ProblemSolvingState.RESOLVED
    assert engine.verification_complete is True


def test_7_12_failed_verification_preserves_remediation_result():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    verification = engine.verify_remediation(
        result=result,
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
    )

    assert verification["verified"] is False
    assert engine.last_remediation_result is not None
    assert engine.last_remediation_result.action_id == result.action_id
    assert engine.last_remediation_result.execution_status == "EXECUTED"


def test_7_12_explicit_recovery_creates_next_cycle():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
    )

    assert engine.workflow.state is WorkflowState.REMEDIATING
    assert engine.recovery_cycle_count == 1

    cycle = engine.start_recovery_cycle()

    assert cycle.cycle_number == 1
    assert engine.recovery_cycles[0].cycle_number == 0
    assert engine.recovery_cycles[1].cycle_number == 1
    assert engine.workflow.state is WorkflowState.INVESTIGATING


def test_7_12_recovery_does_not_execute_remediation():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected={"status": "healthy"},
        observed={"status": "unhealthy"},
    )

    engine.start_recovery_cycle()

    assert engine.workflow.state is WorkflowState.INVESTIGATING
    assert engine.last_remediation_result.execution_status == "EXECUTED"


def test_7_12_terminal_resolution_rejects_new_recovery():
    engine = _make_7_12_eligible_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected={"status": "healthy"},
        observed={"status": "healthy"},
    )

    assert engine.workflow.state is WorkflowState.RESOLVED

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()


def test_7_12_projection_exposes_complete_case_lifecycle():
    engine = _make_7_12_eligible_engine()

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.ACTION_REQUIRED
    assert projection["state"] is ProblemSolvingState.ACTION_REQUIRED
    assert projection["recovery_cycle_count"] == 1
    assert projection["current_recovery_cycle"]["cycle_number"] == 0
    assert projection["verification_complete"] is False
    assert projection["remediation_actions"]
    assert projection["authorizations"]


def test_7_12_case_lifecycle_has_single_canonical_workflow():
    engine = _make_7_12_eligible_engine()

    assert engine.workflow is engine.verification.workflow
    assert engine.workflow.case is engine.case
    assert engine.recovery_history.workflow is engine.workflow


# ============================================================
# Phase 7.13 — Production Lifecycle Failure Boundaries
# ============================================================

def _make_7_13_engine():
    engine = make_engine()

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    engine.evaluate_action_requirement()
    engine.prepare_remediation_authorization()

    return engine


def _prepare_7_13_action(engine):
    action_id = next(iter(engine.remediation_actions))

    action = engine.remediation_actions[action_id]
    action.operation = lambda: None

    return action_id, action


def test_7_13_execution_requires_authorization():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    with pytest.raises(PermissionError):
        engine.execute_remediation(action_id)


def test_7_13_execution_requires_bound_operation():
    engine = _make_7_13_engine()

    action_id = next(iter(engine.remediation_actions))

    engine.authorize_remediation(action_id)

    with pytest.raises(ValueError, match="no bound operation"):
        engine.execute_remediation(action_id)


def test_7_13_verification_requires_executed_result():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)

    # Enter VERIFYING so the execution-status boundary is the
    # boundary under test.
    engine.workflow.start_remediation()
    engine.workflow.start_verification()

    result = RemediationResult(action_id)

    with pytest.raises(ValueError, match="successfully executed"):
        engine.verify_remediation(
            result=result,
            expected="healthy",
            observed="healthy",
        )


def test_7_13_verification_requires_verifying_workflow_state():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    assert engine.workflow.state is WorkflowState.VERIFYING

    engine.workflow.state = WorkflowState.DIAGNOSED

    with pytest.raises(ValueError, match="VERIFYING"):
        engine.verify_remediation(
            result=result,
            expected="healthy",
            observed="healthy",
        )


def test_7_13_failed_verification_does_not_create_recovery_cycle():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    verified = engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert verified["verified"] is False
    assert engine.workflow.state is WorkflowState.REMEDIATING
    assert engine.recovery_cycle_count == 1
    assert engine.current_recovery_cycle.cycle_number == 0


def test_7_13_recovery_requires_remediating_state():
    engine = _make_7_13_engine()

    with pytest.raises(ValueError, match="REMEDIATING"):
        engine.start_recovery_cycle()


def test_7_13_explicit_recovery_creates_next_cycle():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    recovery = engine.start_recovery_cycle()

    assert recovery.cycle_number == 1
    assert recovery.is_recovery is True
    assert engine.workflow.state is WorkflowState.INVESTIGATING
    assert engine.recovery_cycle_count == 2


def test_7_13_recovery_preserves_original_cycle():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    engine.start_recovery_cycle()

    assert engine.recovery_cycles[0].cycle_number == 0
    assert engine.recovery_cycles[0].is_original is True
    assert engine.recovery_cycles[1].cycle_number == 1
    assert engine.recovery_cycles[1].is_recovery is True


def test_7_13_resolved_case_cannot_start_recovery():
    engine = _make_7_13_engine()
    action_id, _ = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert engine.workflow.state is WorkflowState.RESOLVED

    with pytest.raises(ValueError):
        engine.start_recovery_cycle()


def test_7_13_recovery_does_not_execute_remediation():
    engine = _make_7_13_engine()
    action_id, action = _prepare_7_13_action(engine)

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    engine.start_recovery_cycle()

    assert action.execution_status == "EXECUTED"
    assert engine.workflow.state is WorkflowState.INVESTIGATING


def test_7_13_recovery_history_is_defensive():
    engine = _make_7_13_engine()

    cycles = engine.recovery_cycles
    cycles.clear()

    assert engine.recovery_cycle_count == 1
    assert len(engine.recovery_cycles) == 1


# ============================================================
# Phase 7.14 — Production Engine Observability
# ============================================================

def _make_7_14_engine():
    engine = make_engine()

    recommendation = _make_recommendation("HIGH")

    engine.set_result(
        _make_result_with_recommendations(
            [recommendation]
        )
    )

    engine.workflow.start_investigation()
    engine.workflow.mark_diagnosed()

    engine.evaluate_action_requirement()
    engine.prepare_remediation_authorization()

    return engine


def test_7_14_projection_exposes_engine_state():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "state" in projection
    assert projection["state"] == ProblemSolvingState.ACTION_REQUIRED


def test_7_14_projection_exposes_workflow_state():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "workflow_state" in projection
    assert projection["workflow_state"] is WorkflowState.ACTION_REQUIRED


def test_7_14_projection_exposes_diagnostic_result():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "result" in projection
    assert projection["result"] is not None


def test_7_14_projection_exposes_remediation_actions():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "remediation_actions" in projection
    assert len(projection["remediation_actions"]) == 1


def test_7_14_projection_exposes_authorizations():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "authorizations" in projection
    assert len(projection["authorizations"]) == 1


def test_7_14_projection_exposes_execution_boundary():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "execution_available" in projection
    assert projection["execution_available"] is False


def test_7_14_projection_exposes_verification_state():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "verification_result" in projection
    assert projection["verification_result"] is None
    assert projection["verification_complete"] is False


def test_7_14_projection_exposes_recovery_state():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "recovery_cycle_count" in projection
    assert projection["recovery_cycle_count"] == 1

    assert "recovery_cycles" in projection
    assert len(projection["recovery_cycles"]) == 1

    assert "current_recovery_cycle" in projection
    assert projection["current_recovery_cycle"]["cycle_number"] == 0


def test_7_14_projection_exposes_failures():
    engine = _make_7_14_engine()

    projection = engine.projection()

    assert "domain_failures" in projection
    assert projection["domain_failures"] == {}


def test_7_14_projection_is_defensive_for_collections():
    engine = _make_7_14_engine()

    projection = engine.projection()

    projection["remediation_actions"].clear()
    projection["authorizations"].clear()
    projection["recovery_cycles"].clear()
    projection["domain_failures"]["FAKE"] = {
        "type": "FakeError",
        "message": "fake failure",
    }

    fresh = engine.projection()

    assert len(fresh["remediation_actions"]) == 1
    assert len(fresh["authorizations"]) == 1
    assert len(fresh["recovery_cycles"]) == 1
    assert fresh["domain_failures"] == {}


def test_7_14_projection_reflects_authorization_transition():
    engine = _make_7_14_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    before = engine.projection()

    assert before["execution_available"] is False

    action.operation = lambda: None
    engine.authorize_remediation(action_id)

    after = engine.projection()

    assert after["authorizations"][action_id].state.name == "AUTHORIZED"
    assert after["execution_available"] is True


def test_7_14_projection_reflects_execution_transition():
    engine = _make_7_14_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    engine.execute_remediation(action_id)

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.VERIFYING
    assert projection["execution_available"] is False


def test_7_14_projection_reflects_successful_verification():
    engine = _make_7_14_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.RESOLVED
    assert projection["state"] == ProblemSolvingState.RESOLVED
    assert projection["verification_complete"] is True
    assert projection["verification_result"]["verified"] is True


def test_7_14_projection_reflects_failed_verification():
    engine = _make_7_14_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.REMEDIATING
    assert projection["verification_complete"] is False
    assert projection["verification_result"]["verified"] is False
    assert projection["recovery_cycle_count"] == 1


def test_7_14_projection_reflects_explicit_recovery():
    engine = _make_7_14_engine()

    action_id = next(iter(engine.remediation_actions))
    action = engine.remediation_actions[action_id]

    action.operation = lambda: None

    engine.authorize_remediation(action_id)
    result = engine.execute_remediation(action_id)

    engine.verify_remediation(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    engine.start_recovery_cycle()

    projection = engine.projection()

    assert projection["workflow_state"] is WorkflowState.INVESTIGATING
    assert projection["recovery_cycle_count"] == 2
    assert projection["current_recovery_cycle"]["cycle_number"] == 1
    assert projection["current_recovery_cycle"]["is_recovery"] is True


def test_7_14_projection_does_not_change_engine_state():
    engine = _make_7_14_engine()

    before_state = engine.state
    before_workflow = engine.workflow.state
    before_cycles = engine.recovery_cycle_count

    projection = engine.projection()

    assert engine.state is before_state
    assert engine.workflow.state is before_workflow
    assert engine.recovery_cycle_count == before_cycles

    # Reading observability data must remain side-effect free.
    assert projection["state"] is before_state
    assert projection["workflow_state"] is before_workflow
