import pytest

from ui.error_recovery_presentation import ErrorRecoveryPresentation


def test_diagnostic_failure_does_not_claim_system_is_healthy():
    result = ErrorRecoveryPresentation().build_error(
        error_code="DIAGNOSTIC_FAILED"
    )

    assert result["state_type"] == "ERROR"
    assert "state may still be unknown" in result["message"]
    assert result["retry_authorized"] is False


def test_unknown_error_is_safely_normalized():
    result = ErrorRecoveryPresentation().build_error(
        error_code="UNRECOGNIZED_FAILURE"
    )

    assert result["code"] == "UNKNOWN"
    assert result["system_state_confirmed"] is False


def test_empty_state_explains_why_content_is_absent():
    result = ErrorRecoveryPresentation().build_empty(
        empty_code="NO_FINDINGS"
    )

    assert result["state_type"] == "EMPTY"
    assert result["items_available"] is False
    assert result["message"]


def test_recovery_authorization_is_explicit():
    result = ErrorRecoveryPresentation().build_recovery(
        recovery_status="REQUIRES_AUTHORIZATION"
    )

    assert result["requires_authorization"] is True
    assert result["operation_executed_by_presentation"] is False


def test_successful_recovery_requires_verification():
    result = ErrorRecoveryPresentation().build_recovery(
        recovery_status="SUCCEEDED"
    )

    assert result["requires_verification"] is True


def test_recovery_failure_does_not_claim_success():
    result = ErrorRecoveryPresentation().build_recovery(
        recovery_status="FAILED",
        detail="The service did not restart.",
    )

    assert result["status"] == "FAILED"
    assert result["detail"] == "The service did not restart."
    assert "may require investigation" in result["message"]


def test_rejects_invalid_codes_and_detail_types():
    presenter = ErrorRecoveryPresentation()

    with pytest.raises(ValueError):
        presenter.build_error(error_code="")

    with pytest.raises(TypeError):
        presenter.build_error(error_code="UNKNOWN", detail=123)

    with pytest.raises(ValueError):
        presenter.build_empty(empty_code="NOT_A_REAL_STATE")

    with pytest.raises(ValueError):
        presenter.build_recovery(recovery_status="AUTO_RECOVER")


def test_presentation_never_executes_operations():
    presenter = ErrorRecoveryPresentation()

    error = presenter.build_error(error_code="OPERATION_FAILED")
    empty = presenter.build_empty(empty_code="NO_HISTORY")
    recovery = presenter.build_recovery(recovery_status="AVAILABLE")

    assert error["operation_executed_by_presentation"] is False
    assert empty["operation_executed_by_presentation"] is False
    assert recovery["operation_executed_by_presentation"] is False
