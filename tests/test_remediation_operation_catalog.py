from engine.remediation_operation_catalog import (
    RemediationOperationCatalog,
)
from engine.remediation_operation import RemediationOperation


def test_catalog_can_be_created():
    catalog = RemediationOperationCatalog()

    assert catalog is not None


def test_catalog_contains_memory_review_operation():
    catalog = RemediationOperationCatalog()

    operation = catalog.get("memory_review")

    assert isinstance(operation, RemediationOperation)
    assert operation.operation_id == "memory_review"
    assert operation.description


def test_catalog_memory_review_operation_is_not_executed():
    catalog = RemediationOperationCatalog()

    operation = catalog.get("memory_review")

    assert operation.execution_status == "NOT_EXECUTED"


def test_catalog_returns_none_for_unknown_operation():
    catalog = RemediationOperationCatalog()

    assert catalog.get("unknown_operation") is None


def test_catalog_returns_same_registered_operation():
    catalog = RemediationOperationCatalog()

    first = catalog.get("memory_review")
    second = catalog.get("memory_review")

    assert first is second

def test_catalog_can_return_all_operations():
    catalog = RemediationOperationCatalog()

    operations = catalog.get_operations()

    assert isinstance(operations, dict)
    assert "memory_review" in operations


def test_catalog_operations_are_remediation_operations():
    catalog = RemediationOperationCatalog()

    operations = catalog.get_operations()

    for operation in operations.values():
        assert isinstance(operation, RemediationOperation)