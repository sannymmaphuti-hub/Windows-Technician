import pytest

from engine.recommendation import Recommendation
from engine.remediation_result import RemediationResult
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_remediation import TechnicianRemediation
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


class FakeAction:
    action_id = "fake-action-001"
    execution_status = "EXECUTED"


class FakeCoordinator:

    def __init__(self):
        self.calls = []

    def execute(self, action, expected=None, observed=None):
        self.calls.append(
            {
                "action": action,
                "expected": expected,
                "observed": observed,
            }
        )

        result = RemediationResult(
            action_id=action.action_id
        )
        result.execution_status = "EXECUTED"

        return result


class FakePlanner:

    def __init__(self):
        self.calls = []

    def create_action(self, recommendation):
        self.calls.append(recommendation)
        return FakeAction()


class FakeAdapter:

    def __init__(self):
        self.calls = []

    def to_planner_input(self, recommendation):
        self.calls.append(recommendation)

        return {
            "recommendation": recommendation.description,
            "category": recommendation.category,
            "severity": "WARNING",
        }


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(FakeCase())
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    return workflow


@pytest.fixture
def recommendation():
    return Recommendation(
        "memory_review",
        "MEMORY",
        "HIGH",
        "Review memory-intensive processes and close unnecessary applications.",
        "High memory usage may affect system responsiveness.",
    )


@pytest.fixture
def accepted_decision(workflow, recommendation):
    return TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        "Technician approved remediation.",
    )


@pytest.fixture
def remediation(workflow):
    return TechnicianRemediation(workflow)


@pytest.fixture
def fake_components():
    return {
        "adapter": FakeAdapter(),
        "planner": FakePlanner(),
        "coordinator": FakeCoordinator(),
    }


@pytest.fixture
def controlled_remediation(workflow, fake_components):
    return TechnicianRemediation(
        workflow,
        adapter=fake_components["adapter"],
        planner=fake_components["planner"],
        coordinator=fake_components["coordinator"],
    )


def test_remediation_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianRemediation(None)


def test_remediation_exposes_workflow(remediation, workflow):
    assert remediation.workflow is workflow


def test_remediation_starts_inactive(remediation):
    assert remediation.is_active is False


def test_remediation_requires_accepted_decision(
    remediation,
    workflow,
    recommendation,
):
    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.REJECT,
    )

    with pytest.raises(ValueError):
        remediation.start(decision)


def test_remediation_requires_action_required_state(
    recommendation,
):
    workflow = TechnicianWorkflow(FakeCase())

    decision = TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    remediation = TechnicianRemediation(workflow)

    with pytest.raises(ValueError):
        remediation.start(decision)


def test_acceptance_starts_remediation(
    remediation,
    accepted_decision,
    workflow,
):
    remediation.start(accepted_decision)

    assert remediation.is_active is True
    assert workflow.state is WorkflowState.REMEDIATING


def test_remediation_preserves_decision(
    remediation,
    accepted_decision,
):
    remediation.start(accepted_decision)

    assert remediation.decision is accepted_decision


def test_remediation_preserves_recommendation(
    remediation,
    accepted_decision,
):
    remediation.start(accepted_decision)

    assert remediation.recommendation is accepted_decision.recommendation


def test_remediation_cannot_start_twice(
    remediation,
    accepted_decision,
):
    remediation.start(accepted_decision)

    with pytest.raises(ValueError):
        remediation.start(accepted_decision)


def test_remediation_requires_decision_object(
    remediation,
):
    with pytest.raises(ValueError):
        remediation.start(None)


def test_remediation_requires_same_workflow(
    remediation,
    recommendation,
):
    other_workflow = TechnicianWorkflow(FakeCase())

    decision = TechnicianDecision(
        other_workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
    )

    with pytest.raises(ValueError):
        remediation.start(decision)


def test_remediation_execute_requires_active_state(
    remediation,
):
    with pytest.raises(ValueError):
        remediation.execute()


def test_execute_translates_recommendation_to_action(
    controlled_remediation,
    accepted_decision,
    fake_components,
):
    controlled_remediation.start(accepted_decision)
    controlled_remediation.execute()

    adapter = fake_components["adapter"]
    planner = fake_components["planner"]

    assert adapter.calls == [
        accepted_decision.recommendation
    ]

    assert len(planner.calls) == 1
    assert planner.calls[0]["recommendation"] == (
        accepted_decision.recommendation.description
    )


def test_execute_uses_remediation_coordinator(
    controlled_remediation,
    accepted_decision,
    fake_components,
):
    controlled_remediation.start(accepted_decision)
    result = controlled_remediation.execute(
        expected="memory usage reduced",
        observed="memory usage reduced",
    )

    coordinator = fake_components["coordinator"]

    assert len(coordinator.calls) == 1
    assert coordinator.calls[0]["action"].action_id == (
        "fake-action-001"
    )
    assert coordinator.calls[0]["expected"] == (
        "memory usage reduced"
    )
    assert coordinator.calls[0]["observed"] == (
        "memory usage reduced"
    )
    assert result.execution_status == "EXECUTED"


def test_successful_execution_advances_to_verification(
    controlled_remediation,
    accepted_decision,
    workflow,
):
    controlled_remediation.start(accepted_decision)

    result = controlled_remediation.execute()

    assert result.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING


def test_successful_execution_completes_remediation(
    controlled_remediation,
    accepted_decision,
):
    controlled_remediation.start(accepted_decision)

    controlled_remediation.execute()

    assert controlled_remediation.is_active is False
    assert controlled_remediation.is_complete is True


def test_execution_preserves_action_and_result(
    controlled_remediation,
    accepted_decision,
):
    controlled_remediation.start(accepted_decision)

    result = controlled_remediation.execute()

    assert controlled_remediation.action.action_id == (
        "fake-action-001"
    )
    assert controlled_remediation.result is result


def test_execution_cannot_run_twice(
    controlled_remediation,
    accepted_decision,
):
    controlled_remediation.start(accepted_decision)
    controlled_remediation.execute()

    with pytest.raises(ValueError):
        controlled_remediation.execute()


def test_execution_does_not_mutate_recommendation(
    controlled_remediation,
    accepted_decision,
):
    recommendation = accepted_decision.recommendation

    original_priority = recommendation.priority
    original_description = recommendation.description

    controlled_remediation.start(accepted_decision)
    controlled_remediation.execute()

    assert recommendation.priority == original_priority
    assert recommendation.description == original_description


def test_execution_does_not_replace_decision(
    controlled_remediation,
    accepted_decision,
):
    controlled_remediation.start(accepted_decision)
    controlled_remediation.execute()

    assert controlled_remediation.decision is accepted_decision