from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.remediation_result import RemediationResult
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_remediation import TechnicianRemediation
from engine.technician_verification import TechnicianVerification
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeAdapter:
    def to_planner_input(self, recommendation):
        return {
            "recommendation": recommendation.description,
            "category": recommendation.category,
            "severity": "WARNING",
        }


class FakeAction:
    def __init__(self, action_id):
        self.action_id = action_id


class FakePlanner:
    def __init__(self):
        self.counter = 0

    def create_action(self, planner_input):
        self.counter += 1
        return FakeAction(
            f"remediation-action-{self.counter}"
        )


class FakeCoordinator:
    def __init__(self):
        self.results = []
        self.calls = []

    def queue_result(self, execution_status="EXECUTED"):
        result = RemediationResult(
            action_id=f"result-{len(self.results) + 1}"
        )
        result.execution_status = execution_status
        self.results.append(result)

    def execute(self, action, expected=None, observed=None):
        self.calls.append(
            {
                "action": action,
                "expected": expected,
                "observed": observed,
            }
        )

        if self.results:
            result = self.results.pop(0)
        else:
            result = RemediationResult(
                action_id=action.action_id
                if hasattr(action, "action_id")
                else "default-result"
            )
            result.execution_status = "EXECUTED"

        return result


class FakeVerifier:

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def verify(self, expected, observed, action_id):
        self.calls.append(
            {
                "expected": expected,
                "observed": observed,
                "action_id": action_id,
            }
        )

        verified = self.outcomes.pop(0)

        result = RemediationResult(action_id)

        result.verification_result = {
            "verified": verified,
            "expected": expected,
            "observed": observed,
        }

        return result

def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def build_decision(workflow):
    return TechnicianDecision(
        workflow=workflow,
        recommendation=build_recommendation(),
        decision_type=TechnicianDecisionType.ACCEPT,
        notes="Recommendation accepted for remediation.",
    )


def build_remediation(workflow, coordinator):
    return TechnicianRemediation(
        workflow=workflow,
        adapter=FakeAdapter(),
        planner=FakePlanner(),
        coordinator=coordinator,
    )


def build_verification(workflow, outcomes):
    return TechnicianVerification(
        workflow=workflow,
        verifier=FakeVerifier(outcomes),
    )


def prepare_action_required(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()


def test_failed_verification_returns_workflow_to_remediating():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()

    verified = verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert verified is False
    assert workflow.state is WorkflowState.REMEDIATING


def test_failed_verification_does_not_resolve_workflow():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()

    verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert workflow.state is not WorkflowState.RESOLVED
    assert workflow.is_terminal is False


def test_failed_verification_marks_verification_incomplete():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()

    verified = verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert verified is False
    assert verification.is_complete is False
    assert verification.is_active is False


def test_failed_verification_retains_remediation_result():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert verification.result is result
    assert verification.result.action_id == result.action_id


def test_failed_verification_requires_new_remediation_attempt():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert workflow.state is WorkflowState.REMEDIATING

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)

    assert second_remediation.is_active is True
    assert workflow.state is WorkflowState.REMEDIATING


def test_completed_remediation_object_cannot_be_restarted():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    remediation.execute()

    try:
        remediation.start(decision)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Completed remediation was incorrectly restarted."
        )


def test_new_remediation_attempt_uses_same_workflow():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)

    assert first_remediation.workflow is workflow
    assert second_remediation.workflow is workflow


def test_failed_verification_preserves_original_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert decision.recommendation is remediation.recommendation


def test_retry_can_execute_new_remediation():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)
    second_result = second_remediation.execute()

    assert second_result.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING


def test_retry_has_independent_remediation_result():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)
    second_result = second_remediation.execute()

    assert second_result is not first_result
    assert second_result.action_id != first_result.action_id


def test_failed_first_verification_can_be_followed_by_successful_second_verification():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    first_verification = build_verification(
        workflow,
        outcomes=[False],
    )

    first_verification.start()
    first_verified = first_verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert first_verified is False
    assert workflow.state is WorkflowState.REMEDIATING

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)
    second_result = second_remediation.execute()

    second_verification = build_verification(
        workflow,
        outcomes=[True],
    )

    second_verification.start()
    second_verified = second_verification.verify(
        result=second_result,
        expected="healthy",
        observed="healthy",
    )

    assert second_verified is True
    assert second_verification.is_complete is True
    assert workflow.state is WorkflowState.RESOLVED


def test_successful_retry_makes_workflow_terminal():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    first_verification = build_verification(
        workflow,
        outcomes=[False],
    )

    first_verification.start()
    first_verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)
    second_result = second_remediation.execute()

    second_verification = build_verification(
        workflow,
        outcomes=[True],
    )

    second_verification.start()
    second_verification.verify(
        result=second_result,
        expected="healthy",
        observed="healthy",
    )

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_verification_failure_preserves_workflow_history():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")

    remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    remediation.start(decision)
    result = remediation.execute()

    history_before_verification = list(workflow.history)

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    assert workflow.history == (
        history_before_verification
        + [
            (
                WorkflowState.VERIFYING,
                WorkflowState.REMEDIATING,
            )
        ]
    )


def test_recovery_preserves_same_workflow_identity():
    workflow = build_workflow()
    decision = build_decision(workflow)

    workflow_id = workflow.workflow_id

    coordinator = FakeCoordinator()
    coordinator.queue_result("EXECUTED")
    coordinator.queue_result("EXECUTED")

    first_remediation = build_remediation(
        workflow,
        coordinator,
    )

    prepare_action_required(workflow)

    first_remediation.start(decision)
    first_result = first_remediation.execute()

    first_verification = build_verification(
        workflow,
        outcomes=[False],
    )

    first_verification.start()
    first_verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)

    assert workflow.workflow_id == workflow_id
    assert first_remediation.workflow_id if hasattr(
        first_remediation,
        "workflow_id",
    ) else True
    assert second_remediation.workflow is workflow