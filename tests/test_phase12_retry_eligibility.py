import pytest

from engine.operation_failure_classifier import (
    OperationFailureCategory,
    OperationFailureClassifier,
)
from engine.retry_eligibility_policy import RetryEligibilityPolicy


def make_failure(category):
    return OperationFailureClassifier().classify(
        "operation-1", category, "Observed failure"
    )


def test_retry_requires_all_explicit_conditions():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.TIMEOUT),
        explicitly_retry_safe=True,
        retry_budget_remaining=True,
    )

    assert decision.eligible is True


def test_retry_denied_by_default():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.TIMEOUT)
    )

    assert decision.eligible is False


def test_retry_denied_for_non_retryable_category():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.PERMISSION_DENIED),
        explicitly_retry_safe=True,
        retry_budget_remaining=True,
    )

    assert decision.eligible is False


def test_retry_denied_when_operation_is_not_retry_safe():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.TRANSIENT),
        explicitly_retry_safe=False,
        retry_budget_remaining=True,
    )

    assert decision.eligible is False


def test_retry_denied_when_budget_is_exhausted():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.TIMEOUT),
        explicitly_retry_safe=True,
        retry_budget_remaining=False,
    )

    assert decision.eligible is False


def test_decision_projection_is_readable():
    decision = RetryEligibilityPolicy().evaluate(
        make_failure(OperationFailureCategory.TIMEOUT)
    )

    projection = decision.projection()

    assert projection["operation_id"] == "operation-1"
    assert projection["category"] == "TIMEOUT"
    assert isinstance(projection["reason"], str)


@pytest.mark.parametrize("invalid", [None, object(), "failure"])
def test_invalid_failure_input_is_rejected(invalid):
    with pytest.raises(TypeError):
        RetryEligibilityPolicy().evaluate(invalid)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"explicitly_retry_safe": "yes"},
        {"retry_budget_remaining": 1},
    ],
)
def test_invalid_policy_flags_are_rejected(kwargs):
    with pytest.raises(TypeError):
        RetryEligibilityPolicy().evaluate(
            make_failure(OperationFailureCategory.TIMEOUT),
            **kwargs,
        )
