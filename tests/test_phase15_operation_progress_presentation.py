import pytest

from ui.operation_progress_presentation import (
    OperationProgress,
    OperationProgressPresentation,
)


def test_running_operation_projects_percentage_and_message():
    result = OperationProgressPresentation().build(
        OperationProgress(
            operation_id="op-1",
            status="RUNNING",
            message="Collecting system information",
            percentage=45,
        )
    )

    assert result["status"] == "RUNNING"
    assert result["percentage"] == 45
    assert result["indeterminate"] is False
    assert result["terminal"] is False


def test_unknown_percentage_is_indeterminate():
    result = OperationProgressPresentation().build(
        OperationProgress(
            operation_id="op-2",
            status="RUNNING",
            message="Waiting for Windows response",
        )
    )

    assert result["percentage"] is None
    assert result["indeterminate"] is True


def test_successful_operation_projects_complete_progress():
    result = OperationProgressPresentation().build(
        OperationProgress(
            operation_id="op-3",
            status="SUCCEEDED",
            message="System scan completed",
            percentage=75,
        )
    )

    assert result["percentage"] == 100
    assert result["terminal"] is True


@pytest.mark.parametrize("status", ["FAILED", "CANCELLED"])
def test_failed_or_cancelled_operation_is_terminal(status):
    result = OperationProgressPresentation().build(
        OperationProgress(
            operation_id="op-4",
            status=status,
            message="Operation stopped",
        )
    )

    assert result["terminal"] is True
    assert result["status"] == status


def test_rejects_invalid_percentages():
    with pytest.raises(ValueError):
        OperationProgress("op-5", "RUNNING", "Working", -1)

    with pytest.raises(ValueError):
        OperationProgress("op-5", "RUNNING", "Working", 101)

    with pytest.raises(TypeError):
        OperationProgress("op-5", "RUNNING", "Working", True)


def test_rejects_invalid_status_and_input_type():
    presenter = OperationProgressPresentation()

    with pytest.raises(ValueError, match="unsupported operation status"):
        presenter.build(
            OperationProgress("op-6", "UNKNOWN_STATE", "Working")
        )

    with pytest.raises(TypeError, match="OperationProgress"):
        presenter.build({"status": "RUNNING"})


def test_projection_does_not_execute_operations():
    result = OperationProgressPresentation().build(
        OperationProgress("op-7", "RUNNING", "Working", 10)
    )

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False
