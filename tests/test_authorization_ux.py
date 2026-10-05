from engine.remediation_action import RemediationAction
from engine.authorization_ux import AuthorizationUX


def create_action():
    return RemediationAction(
        action_id="memory_review",
        description="Review applications using excessive memory.",
    )


def test_authorization_ux_can_be_created():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux is not None


def test_authorization_ux_requires_remediation_action():
    try:
        AuthorizationUX(None)
    except ValueError:
        return

    raise AssertionError(
        "AuthorizationUX should require a RemediationAction."
    )


def test_authorization_status_is_unauthorized_initially():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.status == "UNAUTHORIZED"


def test_authorization_ux_exposes_action():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.action is action


def test_authorization_ux_exposes_action_id():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.action_id == "memory_review"


def test_authorization_ux_exposes_description():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.description == (
        "Review applications using excessive memory."
    )


def test_authorization_message_for_unauthorized_action():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.message == (
        "This action requires your authorization "
        "before it can be performed."
    )


def test_authorization_message_for_authorized_action():
    action = create_action()
    action.authorize()

    ux = AuthorizationUX(action)

    assert ux.status == "AUTHORIZED"

    assert ux.message == (
        "This action has been authorized."
    )


def test_authorization_message_for_denied_action():
    action = create_action()
    action.deny()

    ux = AuthorizationUX(action)

    assert ux.status == "DENIED"

    assert ux.message == (
        "This action has been denied."
    )


def test_authorization_ux_does_not_authorize():
    action = create_action()

    ux = AuthorizationUX(action)

    assert not hasattr(ux, "authorize")


def test_authorization_ux_does_not_execute():
    action = create_action()

    ux = AuthorizationUX(action)

    assert not hasattr(ux, "execute")


def test_authorization_ux_does_not_remediate():
    action = create_action()

    ux = AuthorizationUX(action)

    assert not hasattr(ux, "remediate")


def test_authorization_ux_does_not_change_action_state():
    action = create_action()

    ux = AuthorizationUX(action)

    assert action.authorization_status == "UNAUTHORIZED"

    _ = ux.status
    _ = ux.message

    assert action.authorization_status == "UNAUTHORIZED"


def test_authorization_ux_reflects_current_action_state():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.status == "UNAUTHORIZED"

    action.authorize()

    assert ux.status == "AUTHORIZED"

    action.deny()

    assert ux.status == "DENIED"