import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QDialog

from engine.remediation_confirmation_dialog import (
    RemediationConfirmationDialog,
)
from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)


@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication

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
        "risk": "MEDIUM",
        "authorization_status": "UNAUTHORIZED",
        "execution_status": "NOT_EXECUTED",
    }

    action.update(overrides)

    return RemediationPresentationModel(action)


def test_requires_presentation_model(qapp):
    with pytest.raises(ValueError):
        RemediationConfirmationDialog(None)


def test_dialog_has_expected_identity(qapp):
    dialog = RemediationConfirmationDialog(make_model())

    assert dialog.objectName() == "remediationConfirmationDialog"
    assert dialog.windowTitle() == "Review Remediation"


def test_dialog_displays_action_details(qapp):
    dialog = RemediationConfirmationDialog(make_model())

    assert dialog.title_label.text() == "Review memory pressure"
    assert dialog.explanation_label.text() == (
        "Memory usage is elevated."
    )
    assert dialog.risk_label.text() == "Risk: MEDIUM"
    assert dialog.authorization_label.text() == (
        "Current authorization: UNAUTHORIZED"
    )
    assert dialog.action_label.text() == (
        "Proposed action: memory_review"
    )


def test_dialog_explains_execution_boundary(qapp):
    dialog = RemediationConfirmationDialog(make_model())

    assert "existing remediation workflow" in (
        dialog.warning_label.text()
    )


def test_dialog_has_approve_and_cancel_buttons(qapp):
    dialog = RemediationConfirmationDialog(make_model())

    assert dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    ).text() == "Approve"

    assert dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    ).text() == "Cancel"


def test_approve_emits_decision(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    received = []
    dialog.decision_made.connect(
        lambda selected_model, approved: received.append(
            (selected_model, approved)
        )
    )

    dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    ).click()

    assert received == [(model, True)]
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_cancel_emits_decision(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    received = []
    dialog.decision_made.connect(
        lambda selected_model, approved: received.append(
            (selected_model, approved)
        )
    )

    dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    ).click()

    assert received == [(model, False)]
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_approve_does_not_change_authorization(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    ).click()

    assert model.authorization_status() == "UNAUTHORIZED"


def test_approve_does_not_change_execution(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    ).click()

    assert model.execution_status() == "NOT_EXECUTED"


def test_cancel_does_not_change_authorization(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    ).click()

    assert model.authorization_status() == "UNAUTHORIZED"


def test_cancel_does_not_change_execution(qapp):
    model = make_model()
    dialog = RemediationConfirmationDialog(model)

    dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    ).click()

    assert model.execution_status() == "NOT_EXECUTED"


def test_dialog_has_no_remediation_execution_surface(qapp):
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
        for name in dir(RemediationConfirmationDialog)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)
