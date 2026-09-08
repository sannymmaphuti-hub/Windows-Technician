from engine.remediation_operation import RemediationOperation


def test_remediation_operation_can_be_created():
    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
    )

    assert operation.operation_id == "memory_review"
    assert operation.description == "Review memory usage."


def test_remediation_operation_starts_unexecuted():
    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
    )

    assert operation.execution_status == "NOT_EXECUTED"


def test_remediation_operation_requires_callable_handler():
    operation = RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=lambda: None,
    )

    assert callable(operation.handler)


def test_remediation_operation_does_not_execute_on_creation():
    state = {"executed": False}

    def handler():
        state["executed"] = True

    RemediationOperation(
        operation_id="memory_review",
        description="Review memory usage.",
        handler=handler,
    )

    assert state["executed"] is False