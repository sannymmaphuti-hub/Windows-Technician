from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.remediation_result import RemediationResult
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


def execute_successful_remediation(workflow, decision, coordinator):
    remediation = build_remediation(
        workflow,
        coordinator,
    )

    remediation.start(decision)
    result = remediation.execute(
        expected="healthy",
        observed="healthy",
    )

    return remediation, result


def test_history_starts_with_cycle_zero():
    workflow = build_workflow()

    history = TechnicianRecoveryCycleHistory(workflow)

    assert history.cycle_count == 1
    assert history.cycles[0].cycle_number == 0
    assert history.latest_cycle.cycle_number == 0


def test_recovery_history_belongs_to_workflow():
    workflow = build_workflow()

    history = TechnicianRecoveryCycleHistory(workflow)

    assert history.workflow is workflow
    assert history.latest_cycle.workflow is workflow


def test_failed_verification_leaves_workflow_in_remediating():
    workflow = build_workflow()
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_successful_remediation(
        workflow,
        decision,
        coordinator,
    )

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


def test_failed_verification_does_not_create_cycle_implicitly():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_successful_remediation(
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

    assert history.cycle_count == 1


def test_second_cycle_can_be_created_for_same_workflow():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    second_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(second_cycle)

    assert history.cycle_count == 2
    assert history.latest_cycle is second_cycle


def test_second_cycle_is_sequential():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    second_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(second_cycle)

    assert history.cycles[-1].cycle_number == 1


def test_failed_verification_can_be_followed_by_recording_recovery_cycle():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)
    decision = build_decision(workflow)

    coordinator = FakeCoordinator()
    coordinator.queue_result()

    prepare_action_required(workflow)

    _, result = execute_successful_remediation(
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

    recovery_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(recovery_cycle)

    assert workflow.state is WorkflowState.REMEDIATING
    assert history.cycle_count == 2
    assert history.latest_cycle is recovery_cycle


def test_recovery_cycle_does_not_change_workflow_state():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    state_before = workflow.state

    recovery_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(recovery_cycle)

    assert workflow.state is state_before


def test_recovery_cycle_does_not_change_workflow_history():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    history_before = list(workflow.history)

    recovery_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(recovery_cycle)

    assert workflow.history == history_before


def test_recovery_cycle_belongs_to_same_workflow():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    recovery_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(recovery_cycle)

    assert recovery_cycle.workflow is workflow
    assert history.latest_cycle.workflow is workflow


def test_foreign_workflow_recovery_cycle_is_rejected():
    workflow = build_workflow()
    foreign_workflow = build_workflow()

    history = TechnicianRecoveryCycleHistory(workflow)

    foreign_cycle = TechnicianRecoveryCycle(
        foreign_workflow,
        cycle_number=1,
    )

    try:
        history.record_cycle(foreign_cycle)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Foreign workflow recovery cycle was accepted."
        )

    assert history.cycle_count == 1


def test_nonsequential_recovery_cycle_is_rejected():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    invalid_cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=3,
    )

    try:
        history.record_cycle(invalid_cycle)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Non-sequential recovery cycle was accepted."
        )

    assert history.cycle_count == 1


def test_duplicate_recovery_cycle_is_rejected():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    try:
        history.record_cycle(cycle)
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Duplicate recovery cycle was accepted."
        )

    assert history.cycle_count == 2


def test_multiple_recovery_cycles_remain_sequential():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )
    third = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    history.record_cycle(second)
    history.record_cycle(third)

    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == [0, 1, 2]


def test_recovery_history_preserves_original_cycle_zero():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    original_cycle = history.cycles[0]

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(second)

    assert history.cycles[0] is original_cycle
    assert history.cycles[0].cycle_number == 0


def test_recovery_cycle_history_identity_is_stable():
    workflow = build_workflow()
    history = TechnicianRecoveryCycleHistory(workflow)

    history_identity = id(history)

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(second)

    assert id(history) == history_identity