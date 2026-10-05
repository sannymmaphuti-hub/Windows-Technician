from engine.remediation_action import RemediationAction
from engine.remediation_preview import RemediationPreview


def create_action():
    return RemediationAction(
        action_id="memory_review",
        description="Review applications using excessive memory.",
    )


def test_preview_can_be_created():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview is not None


def test_preview_requires_remediation_action():
    try:
        RemediationPreview(None)
    except ValueError:
        return

    raise AssertionError(
        "RemediationPreview should require a RemediationAction."
    )


def test_preview_exposes_action():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.action is action


def test_preview_exposes_action_id():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.action_id == "memory_review"


def test_preview_exposes_description():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.description == (
        "Review applications using excessive memory."
    )


def test_preview_exposes_authorization_status():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.authorization_status == "UNAUTHORIZED"


def test_preview_reports_authorization_required():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.requires_authorization is True


def test_preview_reflects_authorized_state():
    action = create_action()
    action.authorize()

    preview = RemediationPreview(action)

    assert preview.authorization_status == "AUTHORIZED"


def test_preview_reflects_denied_state():
    action = create_action()
    action.deny()

    preview = RemediationPreview(action)

    assert preview.authorization_status == "DENIED"


def test_preview_does_not_authorize():
    action = create_action()

    preview = RemediationPreview(action)

    assert not hasattr(preview, "authorize")


def test_preview_does_not_execute():
    action = create_action()

    preview = RemediationPreview(action)

    assert not hasattr(preview, "execute")


def test_preview_does_not_remediate():
    action = create_action()

    preview = RemediationPreview(action)

    assert not hasattr(preview, "remediate")


def test_preview_does_not_change_authorization():
    action = create_action()

    preview = RemediationPreview(action)

    _ = preview.authorization_status
    _ = preview.requires_authorization

    assert action.authorization_status == "UNAUTHORIZED"


def test_preview_preserves_action_identity():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.action is action