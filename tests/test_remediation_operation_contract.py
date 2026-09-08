from engine.remediation_operation import RemediationOperation


def test_remediation_operation_requires_operation_id():
    try:
        RemediationOperation(
            operation_id=None,
            description="Test operation",
        )
    except ValueError:
        return

    assert False, "RemediationOperation should require operation_id"


def test_remediation_operation_requires_description():
    try:
        RemediationOperation(
            operation_id="test_operation",
            description=None,
        )
    except ValueError:
        return

    assert False, "RemediationOperation should require description"


def test_remediation_operation_accepts_missing_handler():
    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
    )

    assert operation.handler is None
    assert operation.execution_status == "NOT_EXECUTED"


def test_remediation_operation_rejects_non_callable_handler():
    try:
        RemediationOperation(
            operation_id="test_operation",
            description="Test operation",
            handler="not_callable",
        )
    except ValueError:
        return

    assert False, "Non-callable handler should be rejected"


def test_remediation_operation_preserves_valid_handler():
    handler = lambda: None

    operation = RemediationOperation(
        operation_id="test_operation",
        description="Test operation",
        handler=handler,
    )

    assert operation.handler is handler