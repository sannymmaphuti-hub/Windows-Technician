# ==========================================
# Windows Technician v0.6
# REMEDIATION FAILURE MODEL TESTS
# ==========================================

from engine.remediation_action import RemediationAction
from engine.remediation_executor import RemediationExecutor


def test_failed_action_records_failed_execution_status():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "FAILED"
    assert action.execution_status == "FAILED"


def test_failed_action_does_not_report_success():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status != "EXECUTED"


def test_failed_action_cannot_be_executed_again():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    executor = RemediationExecutor()

    first_result = executor.execute(action)
    second_result = executor.execute(action)

    assert first_result.execution_status == "FAILED"
    assert second_result.execution_status == "FAILED"


def test_failed_action_has_no_verification_result():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "FAILED"
    assert result.verification_result is None


def test_failed_action_preserves_action_id():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.action_id == "test_action"

def test_failed_result_records_failure_reason():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "FAILED"
    assert result.reason is not None


def test_failed_result_contains_failure_information():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "FAILED"
    assert "test failure" in str(result.reason)


def test_successful_result_has_no_failure_reason():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: None,
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "EXECUTED"
    assert result.reason is None


def test_failed_result_has_no_verification():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("test failure")
        ),
    )

    result = RemediationExecutor().execute(action)

    assert result.execution_status == "FAILED"
    assert result.reason is not None
    assert result.verification_result is None

