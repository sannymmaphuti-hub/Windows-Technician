from engine.remediation_action import RemediationAction
from engine.remediation_coordinator import RemediationCoordinator


def test_coordinator_can_be_created():
    coordinator = RemediationCoordinator()

    assert coordinator is not None


def test_coordinator_executes_action_and_returns_result():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(action)

    assert result.action_id == "memory_review"
    assert result.execution_status == "EXECUTED"

def test_coordinator_verifies_execution_result():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is True
    assert result.verification_result["action_id"] == "memory_review"

def test_coordinator_does_not_verify_failed_execution():
    coordinator = RemediationCoordinator()

    def failing_operation():
        raise RuntimeError("operation failed")

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=failing_operation,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert result.execution_status == "FAILED"
    assert result.verification_result is None

def test_coordinator_records_failed_verification():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected="healthy",
        observed="critical",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is False
    assert result.verification_result["expected"] == "healthy"
    assert result.verification_result["observed"] == "critical"

def test_coordinator_does_not_verify_unauthorized_action():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    result = coordinator.execute(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert result.execution_status == "NOT_EXECUTED"
    assert result.verification_result is None

def test_coordinator_returns_complete_remediation_result():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert result.action_id == "memory_review"
    assert result.execution_status == "EXECUTED"
    assert result.verification_result is not None
    assert result.verification_result["action_id"] == "memory_review"
    assert result.verification_result["verified"] is True

def test_coordinator_does_not_verify_when_expected_is_missing():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected=None,
        observed="healthy",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result is None


def test_coordinator_does_not_verify_when_observed_is_missing():
    coordinator = RemediationCoordinator()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = coordinator.execute(
        action,
        expected="healthy",
        observed=None,
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result is None