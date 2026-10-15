import pytest

from engine.operation_failure_classifier import (
    OperationFailureCategory,
    OperationFailureClassifier,
)


@pytest.mark.parametrize(
    ("category", "candidate"),
    [
        (OperationFailureCategory.TRANSIENT, True),
        (OperationFailureCategory.TIMEOUT, True),
        (OperationFailureCategory.RESOURCE_UNAVAILABLE, True),
        (OperationFailureCategory.PERMISSION_DENIED, False),
        (OperationFailureCategory.INVALID_REQUEST, False),
        (OperationFailureCategory.UNSUPPORTED, False),
        (OperationFailureCategory.UNKNOWN, False),
    ],
)
def test_failure_category_has_conservative_retry_guidance(category, candidate):
    failure = OperationFailureClassifier().classify(
        "operation-1", category, "Observed failure"
    )

    assert failure.retryable_candidate is candidate


def test_failure_projection_is_serializable():
    failure = OperationFailureClassifier().classify(
        "operation-2",
        OperationFailureCategory.TIMEOUT,
        "Provider timed out",
    )

    projection = failure.projection()

    assert projection["category"] == "TIMEOUT"
    assert projection["retryable_candidate"] is True


@pytest.mark.parametrize(
    ("operation_id", "category", "reason"),
    [
        ("", OperationFailureCategory.UNKNOWN, "Failure"),
        ("operation-1", "UNKNOWN", "Failure"),
        ("operation-1", OperationFailureCategory.UNKNOWN, ""),
    ],
)
def test_invalid_failure_evidence_is_rejected(operation_id, category, reason):
    with pytest.raises(ValueError):
        OperationFailureClassifier().classify(
            operation_id, category, reason
        )


def test_failure_reason_is_normalized():
    failure = OperationFailureClassifier().classify(
        " operation-3 ",
        OperationFailureCategory.UNKNOWN,
        "  Provider error  ",
    )

    assert failure.operation_id == "operation-3"
    assert failure.reason == "Provider error"
