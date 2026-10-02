from engine.diagnostic_case import DiagnosticCase
from engine.remediation_result import RemediationResult
from engine.recommendation import Recommendation
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
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
            f"recovery-action-{self.counter}"
        )


class FakeCoordinator:

    def __init__(self):
        self.results = []

    def queue_result(self):
        result = RemediationResult(
            action_id=f"recovery-result-{len(self.results) + 1}"
        )
        result.execution_status = "EXECUTED"
        self.results.append(result)

    def execute(self, action, expected=None, observed=None):
        return self.results.pop(0)


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


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


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
        notes="Recommendation accepted.",
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


def execute_remediation(
    workflow,
    decision,
    coordinator,
):
    remediation = build_remediation(
        workflow,
        coordinator,
    )

    remediation.start(decision)

    result = remediation.execute(
        expected="healthy",
        observed="still_unhealthy",
    )

    return remediation, result


def test_failed_verification_can_create_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    remediation, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()

    verification_result = verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    recovery_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(recovery_cycle)

    assert verification_result is False
    assert history.latest_cycle is recovery_cycle


def test_recovery_cycle_preserves_failed_verification_result():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification.start()

    verification_result = verification.verify(
        result=result,
        expected="healthy",
        observed="still_unhealthy",
    )

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert verification_result is False


def test_recovery_cycle_does_not_replace_remediation_result():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

    result_identity = id(result)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert id(result) == result_identity


def test_recovery_cycle_does_not_change_workflow_after_failed_verification():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

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

    state_before = workflow.state

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert workflow.state is state_before


def test_recovery_cycle_does_not_change_workflow_history_after_failed_verification():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

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

    history_before = list(workflow.history)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert workflow.history == history_before


def test_recovery_cycle_belongs_to_workflow_after_failed_verification():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

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

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert cycle.workflow is workflow
    assert history.workflow is workflow


def test_recovery_cycle_does_not_execute_remediation():
    workflow = build_workflow()
    history = build_history(workflow)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert history.cycle_count == 2


def test_recovery_cycle_does_not_execute_verification():
    workflow = build_workflow()
    history = build_history(workflow)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert history.cycle_count == 2


def test_second_remediation_can_follow_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()
    coordinator.queue_result()

    prepare_action_required(workflow)

    remediation, first_result = execute_remediation(
        workflow,
        decision,
        coordinator,
    )

    verification = build_verification(
        workflow,
        outcomes=[False, True],
    )

    verification.start()

    first_verification = verification.verify(
        result=first_result,
        expected="healthy",
        observed="still_unhealthy",
    )

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert first_verification is False

    second_remediation = build_remediation(
        workflow,
        coordinator,
    )

    second_remediation.start(decision)

    second_result = second_remediation.execute(
        expected="healthy",
        observed="healthy",
    )

    assert second_result.execution_status == "EXECUTED"


def test_recovery_cycle_history_remains_ordered_across_retry():
    workflow = build_workflow()
    history = build_history(workflow)

    first = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(first)

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    history.record_cycle(second)

    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == [0, 1, 2]


def test_failed_verification_does_not_become_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    assert history.cycle_count == 1
    assert verification is not history


def test_recovery_cycle_does_not_become_verification_result():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert cycle not in history.cycles[:-1]
    assert history.latest_cycle is cycle


def test_recovery_cycle_does_not_change_remediation_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    coordinator = FakeCoordinator()
    remediation = build_remediation(
        workflow,
        coordinator,
    )

    remediation_identity = id(remediation)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert id(remediation) == remediation_identity


def test_recovery_cycle_does_not_change_verification_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    verification = build_verification(
        workflow,
        outcomes=[False],
    )

    verification_identity = id(verification)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    assert id(verification) == verification_identity


def test_recovery_history_can_represent_multiple_failed_recovery_attempts():
    workflow = build_workflow()
    history = build_history(workflow)

    first = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    history.record_cycle(first)
    history.record_cycle(second)

    assert history.cycle_count == 3
    assert history.latest_cycle is second