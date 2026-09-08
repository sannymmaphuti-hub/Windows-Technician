from engine.remediation_result import RemediationResult


def test_remediation_result_can_be_created():
    result = RemediationResult(
        action_id="memory_review",
    )

    assert result is not None


def test_remediation_result_preserves_action_id():
    result = RemediationResult(
        action_id="memory_review",
    )

    assert result.action_id == "memory_review"


def test_remediation_result_starts_with_not_executed_status():
    result = RemediationResult(
        action_id="memory_review",
    )

    assert result.execution_status == "NOT_EXECUTED"


def test_remediation_result_starts_without_verification():
    result = RemediationResult(
        action_id="memory_review",
    )

    assert result.verification_result is None

def test_remediation_result_can_record_execution_status():
    result = RemediationResult(
        action_id="memory_review",
    )

    result.execution_status = "EXECUTED"

    assert result.execution_status == "EXECUTED"

def test_remediation_result_can_record_verification_result():
    result = RemediationResult(
        action_id="memory_review",
    )

    verification = {
        "action_id": "memory_review",
        "verified": True,
        "expected": True,
        "observed": True,
        "reason": "Observed condition matches expected condition.",
    }

    result.verification_result = verification

    assert result.verification_result == verification

def test_remediation_result_can_record_failed_execution():
    result = RemediationResult(
        action_id="memory_review",
    )

    result.execution_status = "FAILED"

    assert result.execution_status == "FAILED"

def test_result_can_record_verification_outcome():
    result = RemediationResult(
        action_id="memory_review"
    )

    verification = {
        "action_id": "memory_review",
        "verified": True,
        "expected": "healthy",
        "observed": "healthy",
        "reason": "Observed condition matches expected condition.",
    }

    result.verification_result = verification

    assert result.verification_result == verification