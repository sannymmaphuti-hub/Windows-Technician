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

def test_selector_returns_none_for_none_action():
    selector = RemediationOperationSelector()

    operation_id = selector.select(None)

    assert operation_id is None


def test_selector_returns_none_for_unsupported_severity():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
        category="MEMORY",
        severity="INFO",
    )

    operation_id = selector.select(action)

    assert operation_id is None


def test_selector_returns_none_for_unsupported_category():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_005",
        description="Review network usage.",
        category="NETWORK",
        severity="WARNING",
    )

    operation_id = selector.select(action)

    assert operation_id is None


def test_selector_does_not_modify_authorized_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_006",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    action.authorize()

    selector.select(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.operation is None
    assert action.execution_status == "NOT_EXECUTED"


def test_selector_does_not_modify_denied_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_007",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    action.deny()

    selector.select(action)

    assert action.authorization_status == "DENIED"
    assert action.operation is None
    assert action.execution_status == "NOT_EXECUTED"


def test_selector_does_not_modify_executed_action():
    selector = RemediationOperationSelector()

    action = RemediationAction(
        action_id="action_008",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        requires_authorization=False,
        operation=lambda: None,
    )

    action.execute()

    selector.select(action)

    assert action.execution_status == "EXECUTED"
    assert action.operation is not None

def test_selector_does_not_modify_failed_action():
    selector = RemediationOperationSelector()

    def failing_operation():
        raise RuntimeError("operation failed")

    action = RemediationAction(
        action_id="action_009",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
        requires_authorization=False,
        operation=failing_operation,
    )

    action.execute()

    assert action.execution_status == "FAILED"

    operation_id = selector.select(action)

    assert operation_id == "memory_review"
    assert action.execution_status == "FAILED"
    assert action.operation is not None