from engine.remediation_action import RemediationAction
from engine.status_communication import StatusCommunication


def create_action():
    return RemediationAction(
        action_id="memory_review",
        description="Review applications using excessive memory.",
    )


def test_status_communication_can_be_created():
    action = create_action()

    status = StatusCommunication(action)

    assert status is not None


def test_status_communication_requires_remediation_action():
    try:
        StatusCommunication(None)
    except ValueError:
        return

    raise AssertionError(
        "StatusCommunication should require a RemediationAction."
    )


def test_status_communication_exposes_action():
    action = create_action()

    status = StatusCommunication(action)

    assert status.action is action


def test_status_communication_reports_not_executed():
    action = create_action()

    status = StatusCommunication(action)

    assert status.execution_status == "NOT_EXECUTED"


def test_status_communication_reports_not_executed_message():
    action = create_action()

    status = StatusCommunication(action)

    assert status.message == (
        "This action has not been executed."
    )


def test_status_communication_reports_executed():
    action = create_action()
    action.authorize()

    operation = lambda: None
    action.operation = operation
    action.execute()

    status = StatusCommunication(action)

    assert status.execution_status == "EXECUTED"


def test_status_communication_reports_executed_message():
    action = create_action()
    action.authorize()

    action.operation = lambda: None
    action.execute()

    status = StatusCommunication(action)

    assert status.message == (
        "This action was executed successfully. "
        "Verification is still required."
    )


def test_status_communication_reports_failed():
    action = create_action()
    action.authorize()

    def failing_operation():
        raise RuntimeError("test failure")

    action.operation = failing_operation
    action.execute()

    status = StatusCommunication(action)

    assert status.execution_status == "FAILED"


def test_status_communication_reports_failed_message():
    action = create_action()
    action.authorize()

    def failing_operation():
        raise RuntimeError("test failure")

    action.operation = failing_operation
    action.execute()

    status = StatusCommunication(action)

    assert status.message == (
        "This action could not be completed."
    )


def test_status_communication_does_not_execute():
    action = create_action()

    status = StatusCommunication(action)

    assert not hasattr(status, "execute")


def test_status_communication_does_not_authorize():
    action = create_action()

    status = StatusCommunication(action)

    assert not hasattr(status, "authorize")


def test_status_communication_does_not_verify():
    action = create_action()

    status = StatusCommunication(action)

    assert not hasattr(status, "verify")


def test_status_communication_does_not_change_action():
    action = create_action()

    status = StatusCommunication(action)

    _ = status.execution_status
    _ = status.message

    assert action.execution_status == "NOT_EXECUTED"
    assert action.authorization_status == "UNAUTHORIZED"


def test_status_communication_reflects_current_state():
    action = create_action()

    status = StatusCommunication(action)

    assert status.execution_status == "NOT_EXECUTED"

    action.authorize()
    action.operation = lambda: None
    action.execute()

    assert status.execution_status == "EXECUTED"