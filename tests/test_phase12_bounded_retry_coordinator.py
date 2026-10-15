import pytest

from engine.bounded_retry_coordinator import BoundedRetryCoordinator
from engine.operation_failure_classifier import (
    OperationFailureCategory,
    OperationFailureClassifier,
)


def make_failure(operation_id="operation-1", category=OperationFailureCategory.TIMEOUT):
    return OperationFailureClassifier().classify(
        operation_id, category, "Observed failure"
    )


def test_eligible_retry_is_approved_and_counted():
    coordinator = BoundedRetryCoordinator(maximum_retries=2)

    decision = coordinator.evaluate_retry(
        make_failure(), explicitly_retry_safe=True
    )

    assert decision.approved is True
    assert decision.attempt_number == 1


def test_retry_is_denied_without_explicit_retry_safety():
    decision = BoundedRetryCoordinator().evaluate_retry(make_failure())

    assert decision.approved is False


def test_retry_budget_is_enforced():
    coordinator = BoundedRetryCoordinator(maximum_retries=1)
    failure = make_failure()

    first = coordinator.evaluate_retry(
        failure, explicitly_retry_safe=True
    )
    second = coordinator.evaluate_retry(
        failure, explicitly_retry_safe=True
    )

    assert first.approved is True
    assert second.approved is False
    assert "exhausted" in second.reason.lower()


def test_retry_budget_is_tracked_per_operation():
    coordinator = BoundedRetryCoordinator(maximum_retries=1)

    first = coordinator.evaluate_retry(
        make_failure("operation-1"), explicitly_retry_safe=True
    )
    second = coordinator.evaluate_retry(
        make_failure("operation-2"), explicitly_retry_safe=True
    )

    assert first.approved is True
    assert second.approved is True


def test_non_retryable_failure_is_denied_without_consuming_budget():
    coordinator = BoundedRetryCoordinator(maximum_retries=1)

    denied = coordinator.evaluate_retry(
        make_failure(category=OperationFailureCategory.PERMISSION_DENIED),
        explicitly_retry_safe=True,
    )
    approved = coordinator.evaluate_retry(
        make_failure(), explicitly_retry_safe=True
    )

    assert denied.approved is False
    assert approved.approved is True


def test_history_is_immutable_snapshot():
    coordinator = BoundedRetryCoordinator()
    coordinator.evaluate_retry(make_failure())

    assert isinstance(coordinator.history, tuple)
    assert len(coordinator.history) == 1


def test_invalid_retry_budget_is_rejected():
    for value in (-1, True, 1.5, "2"):
        with pytest.raises(ValueError):
            BoundedRetryCoordinator(maximum_retries=value)


def test_invalid_failure_is_rejected():
    with pytest.raises(TypeError):
        BoundedRetryCoordinator().evaluate_retry(None)


def test_projection_reports_retry_decisions():
    coordinator = BoundedRetryCoordinator(maximum_retries=2)
    coordinator.evaluate_retry(make_failure(), explicitly_retry_safe=True)

    projection = coordinator.projection()

    assert projection["approved_retries"] == 1
    assert len(projection["decisions"]) == 1
