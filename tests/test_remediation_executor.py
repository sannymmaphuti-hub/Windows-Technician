from engine.remediation_action import RemediationAction
from engine.remediation_executor import RemediationExecutor


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