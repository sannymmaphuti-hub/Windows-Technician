from engine.remediation_operation import RemediationOperation
from engine.remediation_operation_catalog import (
    RemediationOperationCatalog,
)
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)


def test_catalog_operations_can_be_registered_in_registry():
    catalog = RemediationOperationCatalog()
    registry = RemediationOperationRegistry()

    operation = catalog.get("memory_review")

    registry.register(
        operation.operation_id,
        operation,
    )

    assert registry.get("memory_review") is operation


def test_catalog_operation_remains_unexecuted_after_registration():
    catalog = RemediationOperationCatalog()
    registry = RemediationOperationRegistry()

    operation = catalog.get("memory_review")

    registry.register(
        operation.operation_id,
        operation,
    )

    assert operation.execution_status == "NOT_EXECUTED"


def test_registry_rejects_duplicate_catalog_operation():
    catalog = RemediationOperationCatalog()
    registry = RemediationOperationRegistry()

    operation = catalog.get("memory_review")

    registry.register(
        operation.operation_id,
        operation,
    )

    try:
        registry.register(
            operation.operation_id,
            operation,
        )
    except ValueError:
        return

    assert False, "Registry should reject duplicate operation IDs"