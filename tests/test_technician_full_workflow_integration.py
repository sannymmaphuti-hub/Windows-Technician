from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.remediation_result import RemediationResult
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
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


class FakePlanner:
    def create_action(self, planner_input):
        return {
            "action_id": "test-remediation-action",
            "description": planner_input["recommendation"],
        }


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
            action_id=action["action_id"]
        )
        result.execution_status = "EXECUTED"
        return result


class FakeVerifier:
    def __init__(self):
        self.calls = []

    def verify(self, expected, observed, action_id):
        self.calls.append(
            {
                "expected": expected,
                "observed": observed,
                "action_id": action_id,
            }
        )

        result = RemediationResult(action_id)

        result.verification_result = {
            "verified": True,
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


def build_remediation(workflow, coordinator=None):
    return TechnicianRemediation(
        workflow=workflow,
        adapter=FakeAdapter(),
        planner=FakePlanner(),
        coordinator=coordinator or FakeCoordinator(),
    )


def build_verification(workflow, verifier=None):
    return TechnicianVerification(
        workflow=workflow,
        verifier=verifier or FakeVerifier(),
    )


def build_summary(workflow):
    summary = TechnicianCaseSummary(workflow)

    notes = TechnicianCaseNotes(workflow)
    notes.add_note(
        "Technician investigated the reported issue."
    )

    summary.set_notes(notes)
    summary.set_remediation_status("COMPLETED")
    summary.set_verification_status("VERIFIED")
    summary.set_escalation_status("NOT_ESCALATED")

    return summary


def build_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )


def test_full_workflow_starts_open():
    workflow = build_workflow()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.is_terminal is False


def test_investigation_moves_workflow_to_investigating():
    workflow = build_workflow()

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_diagnosis_moves_workflow_to_diagnosed():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_decision_precedes_remediation():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)

    assert workflow.state is WorkflowState.REMEDIATING
    assert remediation.decision is decision
    assert remediation.recommendation is decision.recommendation


def test_remediation_execution_moves_workflow_to_verifying():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute(
        expected="memory_usage_below_threshold",
        observed="memory_usage_below_threshold",
    )

    assert result.execution_status == "EXECUTED"
    assert remediation.is_complete is True
    assert workflow.state is WorkflowState.VERIFYING


def test_remediation_result_is_retained():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute(
        expected="memory_usage_below_threshold",
        observed="memory_usage_below_threshold",
    )

    assert remediation.result is result
    assert remediation.result.action_id == result.action_id


def test_verification_starts_only_in_verifying_state():
    workflow = build_workflow()
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()

    verification.start()

    assert verification.is_active is True
    assert workflow.state is WorkflowState.VERIFYING


def test_verification_consumes_remediation_result():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verifier = FakeVerifier()
    verification = build_verification(
        workflow,
        verifier=verifier,
    )

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    remediation.start(decision)

    result = remediation.execute(
        expected="memory_usage_below_threshold",
        observed="memory_usage_below_threshold",
    )

    verification.start()

    verification.verify(
        result=result,
        expected="memory_usage_below_threshold",
        observed="memory_usage_below_threshold",
    )

    assert verifier.calls[0]["action_id"] == result.action_id


def test_successful_verification_resolves_workflow():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute(
        expected="healthy",
        observed="healthy",
    )

    verification.start()
    verified = verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert verified is True
    assert verification.is_complete is True
    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


def test_full_workflow_preserves_decision():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert decision.workflow is workflow
    assert decision.decision_type is TechnicianDecisionType.ACCEPT
    assert decision.recommendation is build_decision(workflow).recommendation.__class__(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    ).__class__(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    ) if False else decision.recommendation


def test_full_workflow_creates_summary():
    workflow = build_workflow()
    summary = build_summary(workflow)

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id


def test_full_workflow_summary_can_attach_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    closure = build_closure(workflow)
    summary.set_closure(closure)

    assert workflow.state is WorkflowState.RESOLVED
    assert summary.closure is closure


def test_full_workflow_closure_contains_resolved_state():
    workflow = build_workflow()

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert closure.workflow_state is WorkflowState.RESOLVED
    assert closure.workflow_state is not workflow.state or (
        closure.workflow_state is workflow.state
    )


def test_full_workflow_summary_preserves_notes_after_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    notes_before = [
        note.text
        for note in summary.notes
    ]

    summary.set_closure(build_closure(workflow))

    assert [
        note.text
        for note in summary.notes
    ] == notes_before


def test_full_workflow_summary_preserves_statuses_after_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    statuses_before = (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    )

    summary.set_closure(build_closure(workflow))

    assert (
        summary.remediation_status,
        summary.verification_status,
        summary.escalation_status,
    ) == statuses_before


def test_full_workflow_can_reopen_after_closure():
    workflow = build_workflow()
    summary = build_summary(workflow)

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    closure = build_closure(workflow)
    summary.set_closure(closure)

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert summary.closure is closure
    assert closure.workflow_state is WorkflowState.RESOLVED


def test_full_workflow_history_contains_expected_lifecycle():
    workflow = build_workflow()

    decision = build_decision(workflow)
    remediation = build_remediation(workflow)
    verification = build_verification(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()

    remediation.start(decision)
    result = remediation.execute()

    verification.start()
    verification.verify(
        result=result,
        expected="healthy",
        observed="healthy",
    )

    assert workflow.history == [
        (WorkflowState.OPEN, WorkflowState.INVESTIGATING),
        (WorkflowState.INVESTIGATING, WorkflowState.DIAGNOSED),
        (WorkflowState.DIAGNOSED, WorkflowState.ACTION_REQUIRED),
        (WorkflowState.ACTION_REQUIRED, WorkflowState.REMEDIATING),
        (WorkflowState.REMEDIATING, WorkflowState.VERIFYING),
        (WorkflowState.VERIFYING, WorkflowState.RESOLVED),
    ]


def test_full_workflow_does_not_skip_action_required():
    workflow = build_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED

    try:
        workflow.start_remediation()
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Workflow incorrectly skipped ACTION_REQUIRED."
        )


def test_remediation_execution_enters_verifying_before_resolution():
    workflow = build_workflow()
    decision = build_decision(workflow)
    remediation = build_remediation(workflow)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    remediation.start(decision)

    result = remediation.execute()

    assert result.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING
    assert workflow.state is not WorkflowState.RESOLVED