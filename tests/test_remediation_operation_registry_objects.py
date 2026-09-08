from engine.remediation_operation import RemediationOperation
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)


def test_registry_can_register_remediation_operation():
    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    registry.register(
        operation.operation_id,
        operation,
    )

    assert registry.get("memory_review") is operation


def test_registry_returns_none_for_unknown_operation():
    registry = RemediationOperationRegistry()

    assert registry.get("unknown_operation") is None


def test_registry_preserves_operation_object():
    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    registry.register(
        "memory_review",
        operation,
    )

    stored = registry.get("memory_review")

    assert stored.operation_id == "memory_review"
    assert stored.description == "Review memory usage."
    assert stored.execution_status == "NOT_EXECUTED"


def test_registry_does_not_execute_registered_operation():
    state = {"executed": False}

    def handler():
        state["executed"] = True

    registry = RemediationOperationRegistry()

    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    registry.register(
        "memory_review",
        operation,
    )

    assert state["executed"] is False