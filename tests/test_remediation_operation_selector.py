import pytest

from engine.remediation_action import RemediationAction
from engine.remediation_operation_selector import (
    RemediationOperationSelector,
)


def test_selector_can_be_created():
    selector = RemediationOperationSelector()

    assert selector is not None


def test_selector_returns_operation_id_for_supported_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    assert operation_id == "memory_review"


def test_selector_returns_none_for_unsupported_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_002",
        description="Investigate CPU usage.",
        category="CPU",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    assert operation_id is None


def test_selector_does_not_modify_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_003",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    selector.select(action)

    assert action.operation is None
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"