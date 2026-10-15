from types import SimpleNamespace

import pytest

import engine.dashboard_diagnostic_controller as controller_module
from engine.dashboard_diagnostic_controller import DashboardDiagnosticController


class FakeRegistry:
    def supported_domains(self):
        return ["memory", "process"]


class FakePlatform:
    def __init__(self):
        self.diagnostic_registry = FakeRegistry()

    def create_case(self):
        return SimpleNamespace()


class FakeWorkflow:
    def __init__(self, case):
        self.case = case


class FakeEngine:
    summary = None
    instances = []

    def __init__(self, *, case, workflow, diagnostic_registry):
        self.case = case
        self.workflow = workflow
        self.diagnostic_registry = diagnostic_registry
        self.solve_calls = []
        self.authorization_calls = 0
        self.execution_calls = 0
        type(self).instances.append(self)

    def solve(self, domains):
        self.solve_calls.append(list(domains))
        return type(self).summary


@pytest.fixture
def fake_production_components(monkeypatch):
    FakeEngine.instances = []
    FakeEngine.summary = {
        "result": SimpleNamespace(
            findings=[{"id": "memory-warning", "severity": "WARNING"}],
            correlations=[{"id": "memory-process-link"}],
            root_causes=[{"cause_type": "RESOURCE_PRESSURE"}],
            recommendations=[{"id": "review-memory-usage"}],
        ),
        "failures": {},
        "domain_results": {"memory": object(), "process": object()},
        "workflow_state": SimpleNamespace(name="INVESTIGATING"),
    }

    monkeypatch.setattr(
        controller_module,
        "TechnicianWorkflow",
        FakeWorkflow,
    )
    monkeypatch.setattr(
        controller_module,
        "ProductionProblemSolvingEngine",
        FakeEngine,
    )

    return FakePlatform


def test_runs_all_registered_domains_through_production_engine(
    fake_production_components,
):
    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )

    outcome = controller.run_diagnostics()

    assert outcome["success"] is True
    assert outcome["partial"] is False
    assert outcome["domains_requested"] == ["memory", "process"]
    assert outcome["domains_completed"] == 2

    engine = FakeEngine.instances[-1]
    assert engine.solve_calls == [["memory", "process"]]
    assert controller.last_case is engine.case
    assert controller.last_workflow is engine.workflow
    assert controller.last_engine is engine


def test_projects_findings_correlations_causes_and_recommendations(
    fake_production_components,
):
    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )

    outcome = controller.run_diagnostics()
    intelligence = outcome["intelligence"]

    assert intelligence["health"]["status"] == "DIAGNOSED"
    assert intelligence["health"]["system_status"] == "WARNING"
    assert intelligence["health"]["score"] == 90
    assert intelligence["system_findings"][0]["id"] == "memory-warning"
    assert intelligence["relationships"][0]["id"] == "memory-process-link"
    assert intelligence["root_causes"][0]["cause_type"] == "RESOURCE_PRESSURE"
    assert intelligence["recommendations"][0]["id"] == "review-memory-usage"


def test_partial_results_are_reported_without_claiming_full_success(
    fake_production_components,
):
    FakeEngine.summary = {
        "result": SimpleNamespace(
            findings=[{"id": "partial-finding"}],
            correlations=[],
            root_causes=[],
            recommendations=[],
        ),
        "failures": {"process": "Diagnostic provider unavailable"},
        "domain_results": {"memory": object()},
        "workflow_state": SimpleNamespace(name="INVESTIGATING"),
    }

    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )

    outcome = controller.run_diagnostics()

    assert outcome["success"] is True
    assert outcome["partial"] is True
    assert outcome["failures"] == {
        "process": "Diagnostic provider unavailable"
    }
    assert outcome["intelligence"]["health"]["status"] == "PARTIAL"
    assert outcome["intelligence"]["health"]["system_status"] == "UNKNOWN"
    assert outcome["intelligence"]["health"]["coverage"] == "PARTIAL"


def test_missing_diagnostic_result_is_reported_as_failure(
    fake_production_components,
):
    FakeEngine.summary = {
        "result": None,
        "failures": {"memory": "Provider failed"},
        "domain_results": {},
        "workflow_state": SimpleNamespace(name="INVESTIGATING"),
    }

    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )

    outcome = controller.run_diagnostics()

    assert outcome["success"] is False
    assert outcome["partial"] is False
    assert outcome["intelligence"]["health"]["status"] == "DIAGNOSTICS FAILED"


def test_controller_does_not_authorize_or_execute_remediation(
    fake_production_components,
):
    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )

    outcome = controller.run_diagnostics()
    engine = FakeEngine.instances[-1]

    assert outcome["success"] is True
    assert engine.authorization_calls == 0
    assert engine.execution_calls == 0
    assert engine.solve_calls == [["memory", "process"]]
def test_deduplicates_recommendations_without_losing_distinct_findings(
    fake_production_components,
):
    duplicate = {
        "type": "FINDING",
        "priority": "HIGH",
        "domain": "MEMORY",
        "action": "Review memory usage",
        "rationale": "Original explanation",
        "finding": {"id": "memory-001", "finding_type": "MEMORY_PRESSURE"},
    }

    same_evidence_different_rationale = {
        **duplicate,
        "rationale": "Additional explanation",
    }

    distinct_finding_same_action = {
        **duplicate,
        "rationale": "Separate finding",
        "finding": {"id": "memory-002", "finding_type": "MEMORY_PRESSURE"},
    }

    FakeEngine.summary = {
        "result": SimpleNamespace(
            findings=[],
            correlations=[],
            root_causes=[],
            recommendations=[duplicate],
        ),
        "failures": {},
        "domain_results": {
            "memory": SimpleNamespace(
                findings=[],
                correlations=[],
                root_causes=[],
                recommendations=[same_evidence_different_rationale],
            ),
            "process": SimpleNamespace(
                findings=[],
                correlations=[],
                root_causes=[],
                recommendations=[distinct_finding_same_action],
            ),
        },
        "workflow_state": SimpleNamespace(name="INVESTIGATING"),
    }

    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )
    outcome = controller.run_diagnostics()

    recommendations = outcome["intelligence"]["recommendations"]
    matching = [
        item for item in recommendations
        if isinstance(item, dict)
        and item.get("type") == "FINDING"
        and item.get("action") == "Review memory usage"
    ]

    finding_ids = {
        item["finding"]["id"]
        for item in matching
    }

    assert finding_ids == {"memory-001", "memory-002"}
    assert len(matching) == 2



def test_dashboard_preserves_recommendation_traceability(
    fake_production_components,
):
    recommendation = {
        "type": "FINDING",
        "priority": "HIGH",
        "domain": "MEMORY",
        "finding_id": "memory-dashboard-001",
        "finding": {
            "id": "memory-dashboard-001",
            "finding_type": "MEMORY_PRESSURE",
        },
        "evidence": [{"source": "memory_monitor", "value": 92}],
        "provenance": {"collector": "memory_engine"},
        "action": "Review memory usage",
        "rationale": "Memory pressure was observed.",
    }

    FakeEngine.summary = {
        "result": SimpleNamespace(
            findings=[],
            correlations=[],
            root_causes=[],
            recommendations=[recommendation],
        ),
        "failures": {},
        "domain_results": {},
        "workflow_state": SimpleNamespace(name="INVESTIGATING"),
    }

    controller = DashboardDiagnosticController(
        platform_factory=fake_production_components
    )
    outcome = controller.run_diagnostics()

    assert outcome["success"] is True
    displayed = outcome["intelligence"]["recommendations"]
    matching = [
        item for item in displayed
        if isinstance(item, dict)
        and item.get("finding_id") == "memory-dashboard-001"
    ]

    assert len(matching) == 1
    assert matching[0]["finding"] == recommendation["finding"]
    assert matching[0]["evidence"] == recommendation["evidence"]
    assert matching[0]["provenance"] == recommendation["provenance"]
