import pytest
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)


def test_registry_can_be_created():
    registry = RemediationOperationRegistry()

    assert registry is not None


def test_registry_starts_empty():
    registry = RemediationOperationRegistry()

    assert registry.get("memory_review") is None


def test_registry_can_register_operation():
    registry = RemediationOperationRegistry()

    operation = lambda: None

    registry.register(
        "memory_review",
        operation,
    )

    assert registry.get("memory_review") is operation

def test_registry_rejects_missing_operation():
    registry = RemediationOperationRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "memory_review",
            None,
        )


def test_registry_rejects_missing_operation_id():
    registry = RemediationOperationRegistry()

    with pytest.raises(ValueError):
        registry.register(
            None,
            lambda: None,
        )

def test_registry_rejects_duplicate_operation_id():
    registry = RemediationOperationRegistry()

    first_operation = lambda: None
    second_operation = lambda: None

    registry.register(
        "memory_review",
        first_operation,
    )

    with pytest.raises(ValueError):
        registry.register(
            "memory_review",
            second_operation,
        )

    assert registry.get("memory_review") is first_operation

def test_registry_returns_registered_operation():
    registry = RemediationOperationRegistry()

    operation = lambda: None

    registry.register(
        "memory_review",
        operation,
    )

    assert registry.get("memory_review") is operation