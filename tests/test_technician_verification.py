import pytest

from engine.remediation_result import RemediationResult
from engine.technician_verification import TechnicianVerification
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class FakeCase:
    case_id = "case-001"
    findings = []
    root_causes = []
    recommendations = []


class FakeVerifier:

    def __init__(self, result=True):
        self.result = result
        self.calls = []

    def verify(self, expected, observed, action_id=None):
        self.calls.append(
            {
                "expected": expected,
                "observed": observed,
                "action_id": action_id,
            }
        )

        result = RemediationResult(action_id)

        result.verification_result = {
            "verified": self.result,
            "expected": expected,
            "observed": observed,
        }

        return result
    
@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(FakeCase())
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    return workflow


@pytest.fixture
def verification(workflow):
    return TechnicianVerification(workflow)


@pytest.fixture
def successful_result():
    result = RemediationResult(
        action_id="action-001"
    )
    result.execution_status = "EXECUTED"
    return result


@pytest.fixture
def failed_result():
    result = RemediationResult(
        action_id="action-001"
    )
    result.execution_status = "FAILED"
    result.reason = "Remediation operation failed."
    return result


def test_verification_requires_workflow():
    with pytest.raises(ValueError):
        TechnicianVerification(None)


def test_verification_exposes_workflow(
    verification,
    workflow,
):
    assert verification.workflow is workflow


def test_verification_starts_inactive(verification):
    assert verification.is_active is False


def test_verification_requires_verifying_state():
    workflow = TechnicianWorkflow(FakeCase())
    verification = TechnicianVerification(workflow)

    with pytest.raises(ValueError):
        verification.start()


def test_verification_can_start(
    verification,
    workflow,
):
    verification.start()

    assert verification.is_active is True
    assert workflow.state is WorkflowState.VERIFYING


def test_verification_cannot_start_twice(
    verification,
):
    verification.start()

    with pytest.raises(ValueError):
        verification.start()


def test_verification_requires_remediation_result(
    verification,
):
    verification.start()

    with pytest.raises(ValueError):
        verification.verify(None, "observed")


def test_successful_verification_resolves_workflow(
    verification,
    successful_result,
    workflow,
):
    verification.start()

    result = verification.verify(
        successful_result,
        expected="memory reduced",
        observed="memory reduced",
    )

    assert result is True
    assert workflow.state is WorkflowState.RESOLVED
    assert verification.is_complete is True
    assert verification.is_active is False


def test_failed_verification_returns_to_remediation(
    verification,
    successful_result,
    workflow,
):
    verification.start()

    result = verification.verify(
        successful_result,
        expected="memory reduced",
        observed="memory still high",
    )

    assert result is False
    assert workflow.state is WorkflowState.REMEDIATING
    assert verification.is_complete is False
    assert verification.is_active is False


def test_verification_uses_existing_verifier(
    verification,
    successful_result,
    workflow,
):
    fake_verifier = FakeVerifier(result=True)

    verification = TechnicianVerification(
        workflow,
        verifier=fake_verifier,
    )

    verification.start()

    result = verification.verify(
        successful_result,
        expected="expected-state",
        observed="observed-state",
    )

    assert result is True
    assert len(fake_verifier.calls) == 1
    assert fake_verifier.calls[0]["expected"] == "expected-state"
    assert fake_verifier.calls[0]["observed"] == "observed-state"
    assert fake_verifier.calls[0]["action_id"] == "action-001"


def test_verification_rejects_non_executed_result(
    verification,
    failed_result,
):
    verification.start()

    with pytest.raises(ValueError):
        verification.verify(
            failed_result,
            expected="expected-state",
            observed="observed-state",
        )


def test_verification_preserves_result(
    verification,
    successful_result,
):
    verification.start()

    verification.verify(
        successful_result,
        expected="expected",
        observed="expected",
    )

    assert verification.result is successful_result


def test_verification_result_is_read_only(
    verification,
    successful_result,
):
    verification.start()

    verification.verify(
        successful_result,
        expected="expected",
        observed="expected",
    )

    with pytest.raises((AttributeError, ValueError)):
        verification.result = None


def test_resolved_workflow_cannot_be_verified_again(
    verification,
    successful_result,
    workflow,
):
    verification.start()

    verification.verify(
        successful_result,
        expected="expected",
        observed="expected",
    )

    assert workflow.state is WorkflowState.RESOLVED

    with pytest.raises(ValueError):
        verification.start()