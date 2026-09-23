# ==========================================
# Windows Technician v0.6
# REMEDIATION RESULT
# ==========================================


from engine.remediation_result import RemediationResult


def test_remediation_result_can_be_created():
    result = RemediationResult("test_action")

    assert result is not None


def test_remediation_result_preserves_action_id():
    result = RemediationResult("test_action")

    assert result.action_id == "test_action"


def test_new_result_starts_not_executed():
    result = RemediationResult("test_action")

    assert result.execution_status == "NOT_EXECUTED"


def test_new_result_has_no_reason():
    result = RemediationResult("test_action")

    assert result.reason is None


def test_new_result_has_no_verification_result():
    result = RemediationResult("test_action")

    assert result.verification_result is None


def test_result_can_record_successful_execution():
    result = RemediationResult("test_action")

    result.execution_status = "EXECUTED"

    assert result.execution_status == "EXECUTED"


def test_result_can_record_failed_execution():
    result = RemediationResult("test_action")

    result.execution_status = "FAILED"

    assert result.execution_status == "FAILED"


def test_result_can_record_rejection_reason():
    result = RemediationResult("test_action")

    result.reason = "NOT_AUTHORIZED"

    assert result.reason == "NOT_AUTHORIZED"


def test_result_can_record_verification():
    result = RemediationResult("test_action")

    verification = {
        "verified": True,
        "action_id": "test_action",
    }

    result.verification_result = verification

    assert result.verification_result == verification

def test_result_rejection_does_not_execute_action():
    result = RemediationResult("test_action")

    result.reason = "NOT_AUTHORIZED"

    assert result.execution_status == "NOT_EXECUTED"


def test_result_failure_has_no_verification_by_default():
    result = RemediationResult("test_action")

    result.execution_status = "FAILED"

    assert result.verification_result is None


def test_result_success_can_have_verification():
    result = RemediationResult("test_action")

    result.execution_status = "EXECUTED"

    result.verification_result = {
        "verified": True,
        "action_id": "test_action",
    }

    assert result.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is True


def test_result_rejection_can_preserve_action_id():
    result = RemediationResult("test_action")

    result.reason = "OPERATION_NOT_BOUND"

    assert result.action_id == "test_action"
    assert result.reason == "OPERATION_NOT_BOUND"


def test_result_failure_can_preserve_action_id():
    result = RemediationResult("test_action")

    result.execution_status = "FAILED"

    assert result.action_id == "test_action"
    assert result.execution_status == "FAILED"

def test_failed_result_does_not_have_successful_verification():
    result = RemediationResult("test_action")

    result.execution_status = "FAILED"

    assert result.verification_result is None


def test_new_result_is_not_verified():
    result = RemediationResult("test_action")

    assert result.verification_result is None


def test_rejected_result_has_no_verification():
    result = RemediationResult("test_action")

    result.reason = "NOT_AUTHORIZED"

    assert result.execution_status == "NOT_EXECUTED"
    assert result.verification_result is None


def test_successful_result_can_be_verified_as_false():
    result = RemediationResult("test_action")

    result.execution_status = "EXECUTED"
    result.verification_result = {
        "verified": False,
        "action_id": "test_action",
    }

    assert result.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is False

