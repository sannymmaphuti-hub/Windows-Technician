from engine.remediation_action import RemediationAction
from engine.remediation_executor import RemediationExecutor
from engine.remediation_eligibility import RemediationEligibility


def test_executor_can_be_created():
    executor = RemediationExecutor()

    assert executor is not None


def test_executor_returns_remediation_result():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = executor.execute(action)

    assert result.action_id == "memory_review"

def test_executor_records_successful_execution():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "EXECUTED"


def test_executor_records_failed_execution():
    executor = RemediationExecutor()

    def failing_operation():
        raise RuntimeError("operation failed")

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=failing_operation,
    )

    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "FAILED"


def test_executor_records_unauthorized_execution():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"

def test_executor_does_not_execute_completed_action_again():
    executor = RemediationExecutor()
    executions = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )

    action.authorize()

    first_result = executor.execute(action)
    second_result = executor.execute(action)

    assert first_result.execution_status == "EXECUTED"
    assert second_result.execution_status == "EXECUTED"
    assert executions == ["run"]

def test_executor_rejects_ineligible_action():
    executor = RemediationExecutor()
    eligibility = RemediationEligibility()
    executions = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )

    assert eligibility.is_eligible(action) is False

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert executions == []

def test_executor_checks_remediation_eligibility_before_execution():
    executor = RemediationExecutor()
    executions = []

    class RejectAllEligibility:
        def is_eligible(self, action):
            return False

    executor.eligibility = RejectAllEligibility()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )
    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert executions == []

def test_executor_reports_eligibility_reason_when_action_is_rejected():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "NOT_AUTHORIZED"

def test_executor_successful_execution_has_no_rejection_reason():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "EXECUTED"
    assert result.reason is None

def test_executor_failed_execution_has_no_eligibility_reason():
    executor = RemediationExecutor()

    def failing_operation():
        raise RuntimeError("operation failed")

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=failing_operation,
    )

    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "FAILED"
    assert result.reason == "operation failed"

def test_executor_reports_operation_not_bound_reason():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
    )

    action.authorize()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "OPERATION_NOT_BOUND"

def test_executor_reports_denied_reason():
    executor = RemediationExecutor()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.deny()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "DENIED"

def test_executor_rejects_invalid_action():
    executor = RemediationExecutor()

    result = executor.execute("not an action")

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "INVALID_ACTION"

def test_executor_rejection_reason_is_not_authorized():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
    )

    executor = RemediationExecutor()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "NOT_AUTHORIZED"


def test_executor_rejection_reason_is_operation_not_bound():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
    )
    action.authorize()

    executor = RemediationExecutor()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "OPERATION_NOT_BOUND"


def test_executor_rejection_reason_is_denied():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
    )
    action.deny()

    executor = RemediationExecutor()

    result = executor.execute(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert result.reason == "DENIED"


def test_executor_success_has_no_rejection_reason():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        operation=lambda: None,
    )
    action.authorize()

    executor = RemediationExecutor()

    result = executor.execute(action)

    assert result.execution_status == "EXECUTED"
    assert result.reason is None