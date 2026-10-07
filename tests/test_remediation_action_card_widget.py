import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPushButton

from engine.remediation_action_card_widget import RemediationActionCardWidget
from engine.remediation_presentation_model import RemediationPresentationModel


@pytest.fixture
def qapp():
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


def make_model(**overrides):
    action = {
        "action_id": "A1",
        "action_type": "memory_review",
        "title": "Review memory pressure",
        "explanation": "Memory usage is elevated.",
        "risk": "medium",
        "authorization_status": "UNAUTHORIZED",
        "execution_status": "NOT_EXECUTED",
    }

    action.update(overrides)

    return RemediationPresentationModel(action)


def test_requires_presentation_model(qapp):
    with pytest.raises(ValueError):
        RemediationActionCardWidget(None)


def test_widget_has_expected_object_name(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.objectName() == "remediationActionCard"


def test_widget_displays_title(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.title_label.text() == "Review memory pressure"


def test_widget_displays_action_type(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.action_type_label.text() == "Action: memory_review"


def test_widget_displays_explanation(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.explanation_label.text() == "Memory usage is elevated."


def test_widget_displays_risk(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.risk_label.text() == "Risk: MEDIUM"


def test_widget_displays_authorization_state(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.authorization_label.text() == (
        "Authorization: UNAUTHORIZED"
    )


def test_widget_displays_execution_state(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.execution_label.text() == (
        "Execution: NOT_EXECUTED"
    )


def test_widget_displays_user_message(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert "requires your authorization" in (
        widget.message_label.text()
    )


def test_review_button_exists(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert isinstance(widget.review_button, QPushButton)
    assert widget.review_button.text() == "Review"


def test_review_button_is_enabled_for_unexecuted_action(qapp):
    widget = RemediationActionCardWidget(make_model())

    assert widget.review_button.isEnabled() is True


def test_review_emits_presentation_model(qapp):
    widget = RemediationActionCardWidget(make_model())

    received = []
    widget.review_requested.connect(received.append)

    widget.review_button.click()

    assert received == [widget.presentation_model]


def test_review_does_not_change_authorization_state(qapp):
    model = make_model()

    widget = RemediationActionCardWidget(model)
    widget.review_button.click()

    assert model.authorization_status() == "UNAUTHORIZED"


def test_review_does_not_change_execution_state(qapp):
    model = make_model()

    widget = RemediationActionCardWidget(model)
    widget.review_button.click()

    assert model.execution_status() == "NOT_EXECUTED"


def test_executed_action_disables_review_button(qapp):
    widget = RemediationActionCardWidget(
        make_model(
            authorization_status="AUTHORIZED",
            execution_status="EXECUTED",
        )
    )

    assert widget.review_button.isEnabled() is False


def test_failed_action_keeps_review_available(qapp):
    widget = RemediationActionCardWidget(
        make_model(
            authorization_status="AUTHORIZED",
            execution_status="FAILED",
        )
    )

    assert widget.review_button.isEnabled() is True


def test_refresh_updates_display(qapp):
    model = make_model()

    widget = RemediationActionCardWidget(model)

    assert widget.risk_label.text() == "Risk: MEDIUM"

    updated = RemediationPresentationModel(
        {
            "action_id": "A1",
            "action_type": "memory_review",
            "title": "Review memory pressure",
            "explanation": "Memory usage is critical.",
            "risk": "HIGH",
            "authorization_status": "AUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        }
    )

    widget.presentation_model = updated
    widget.refresh()

    assert widget.risk_label.text() == "Risk: HIGH"
    assert widget.authorization_label.text() == (
        "Authorization: AUTHORIZED"
    )
    assert widget.explanation_label.text() == (
        "Memory usage is critical."
    )


def test_widget_has_no_remediation_execution_surface(qapp):
    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "retry",
        "verify",
        "run",
    }

    public_methods = {
        name
        for name in dir(RemediationActionCardWidget)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)
