import pytest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from engine.accessibility import AccessibilityHelper
from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_widget import DashboardWidget
from engine.diagnostic_card_model import DiagnosticCardModel
from engine.diagnostic_card_widget import DiagnosticCardWidget
from engine.remediation_action_card_widget import RemediationActionCardWidget
from engine.remediation_confirmation_dialog import (
    RemediationConfirmationDialog,
)
from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)
from engine.main_window import MainWindow


@pytest.fixture
def qapp():
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


def make_diagnostic_model():
    return DiagnosticCardModel(
        {
            "finding_id": "F-001",
            "severity": "HIGH",
            "category": "MEMORY",
            "title": "High memory pressure",
            "explanation": "Memory usage is elevated.",
            "evidence": [{"usage": 88}],
            "next_step": "Review memory-intensive applications.",
        }
    )


def make_remediation_model():
    return RemediationPresentationModel(
        {
            "action_id": "A-001",
            "action_type": "memory_review",
            "title": "Review memory usage",
            "explanation": "Memory pressure should be reviewed.",
            "risk": "LOW",
            "authorization_status": "UNAUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        }
    )


def make_dashboard():
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "WARNING",
                "score": 72,
            },
            "system_findings": [
                {
                    "finding_id": "F-001",
                    "severity": "HIGH",
                    "category": "MEMORY",
                    "title": "High memory pressure",
                    "explanation": "Memory usage is elevated.",
                    "evidence": [{"usage": 88}],
                    "next_step": "Review memory-intensive applications.",
                }
            ],
            "remediation_actions": [
                {
                    "action_id": "A-001",
                    "action_type": "memory_review",
                    "title": "Review memory usage",
                    "explanation": "Memory pressure should be reviewed.",
                    "risk": "LOW",
                    "authorization_status": "UNAUTHORIZED",
                    "execution_status": "NOT_EXECUTED",
                }
            ],
        },
    )

    return DashboardWidget(view_model)


def test_accessibility_helper_requires_widget():
    with pytest.raises(ValueError):
        AccessibilityHelper.describe(
            None,
            "Example",
        )


def test_accessibility_helper_requires_name(qapp):
    label = QLabel()

    with pytest.raises(ValueError):
        AccessibilityHelper.describe(
            label,
            "",
        )


def test_accessibility_helper_sets_name(qapp):
    label = QLabel()

    AccessibilityHelper.describe(
        label,
        "System health",
    )

    assert label.accessibleName() == "System health"


def test_accessibility_helper_sets_description(qapp):
    label = QLabel()

    AccessibilityHelper.describe(
        label,
        "System health",
        "Current overall health status of the computer.",
    )

    assert label.accessibleName() == "System health"
    assert (
        label.accessibleDescription()
        == "Current overall health status of the computer."
    )


def test_accessibility_helper_makes_widget_keyboard_focusable(qapp):
    button = QPushButton()

    AccessibilityHelper.make_focusable(button)

    assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_accessibility_helper_combines_description_and_focus(qapp):
    button = QPushButton()

    AccessibilityHelper.describe_and_focus(
        button,
        "Review remediation",
        "Review the proposed remediation before deciding.",
    )

    assert button.accessibleName() == "Review remediation"
    assert (
        button.accessibleDescription()
        == "Review the proposed remediation before deciding."
    )
    assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_diagnostic_card_has_accessible_identity(qapp):
    card = DiagnosticCardWidget(
        make_diagnostic_model()
    )

    assert card.accessibleName() == "Diagnostic finding"
    assert "diagnostic" in card.accessibleDescription().lower()


def test_diagnostic_card_labels_have_accessible_names(qapp):
    card = DiagnosticCardWidget(
        make_diagnostic_model()
    )

    assert card.severity_label.accessibleName() == "Diagnostic severity"
    assert card.category_label.accessibleName() == "Diagnostic category"
    assert card.title_label.accessibleName() == "Diagnostic finding title"
    assert (
        card.explanation_label.accessibleName()
        == "Diagnostic explanation"
    )
    assert card.evidence_label.accessibleName() == "Diagnostic evidence"
    assert card.next_step_label.accessibleName() == "Diagnostic next step"


def test_remediation_card_has_accessible_identity(qapp):
    card = RemediationActionCardWidget(
        make_remediation_model()
    )

    assert card.accessibleName() == "Remediation action"
    assert "remediation" in card.accessibleDescription().lower()


def test_remediation_review_button_is_accessible(qapp):
    card = RemediationActionCardWidget(
        make_remediation_model()
    )

    assert card.review_button.accessibleName() == "Review remediation"
    assert (
        "proposed remediation"
        in card.review_button.accessibleDescription().lower()
    )
    assert (
        card.review_button.focusPolicy()
        == Qt.FocusPolicy.StrongFocus
    )


def test_remediation_card_labels_have_accessible_names(qapp):
    card = RemediationActionCardWidget(
        make_remediation_model()
    )

    assert card.title_label.accessibleName() == "Remediation title"
    assert (
        card.action_type_label.accessibleName()
        == "Remediation action type"
    )
    assert (
        card.explanation_label.accessibleName()
        == "Remediation explanation"
    )
    assert card.risk_label.accessibleName() == "Remediation risk"
    assert (
        card.authorization_label.accessibleName()
        == "Remediation authorization status"
    )
    assert (
        card.execution_label.accessibleName()
        == "Remediation execution status"
    )
    assert (
        card.message_label.accessibleName()
        == "Remediation status message"
    )


def test_confirmation_dialog_has_accessible_identity(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    assert dialog.accessibleName() == "Remediation confirmation"
    assert "approval" in dialog.accessibleDescription().lower()


def test_confirmation_dialog_labels_have_accessible_names(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    assert dialog.title_label.accessibleName() == "Confirmation title"
    assert (
        dialog.explanation_label.accessibleName()
        == "Confirmation explanation"
    )
    assert dialog.risk_label.accessibleName() == "Confirmation risk"
    assert (
        dialog.authorization_label.accessibleName()
        == "Current authorization status"
    )
    assert (
        dialog.action_label.accessibleName()
        == "Proposed remediation action"
    )
    assert (
        dialog.warning_label.accessibleName()
        == "Remediation approval warning"
    )


def test_confirmation_dialog_buttons_are_keyboard_accessible(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    approve = dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    )
    cancel = dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    )

    assert approve.accessibleName() == "Approve remediation"
    assert cancel.accessibleName() == "Cancel remediation"

    assert approve.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert cancel.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_dashboard_has_accessible_identity(qapp):
    dashboard = make_dashboard()

    assert dashboard.accessibleName() == "Windows Technician dashboard"
    assert "dashboard" in dashboard.accessibleDescription().lower()


def test_dashboard_sections_have_accessible_names(qapp):
    dashboard = make_dashboard()

    assert (
        dashboard.health_status_label.accessibleName()
        == "System health status"
    )
    assert (
        dashboard.health_score_label.accessibleName()
        == "System health score"
    )
    assert (
        dashboard.findings_label.accessibleName()
        == "Diagnostic finding count"
    )
    assert (
        dashboard.relationships_label.accessibleName()
        == "System relationships"
    )
    assert (
        dashboard.root_causes_label.accessibleName()
        == "System root causes"
    )
    assert (
        dashboard.recommendations_label.accessibleName()
        == "System recommendations"
    )


def test_dashboard_title_is_accessible(qapp):
    dashboard = make_dashboard()

    assert dashboard.title_label.accessibleName() == "Dashboard title"


def test_main_window_has_accessible_identity(qapp):
    state = ApplicationState()

    window = MainWindow(state)

    assert window.accessibleName() == "Windows Technician main window"
    assert "application" in window.accessibleDescription().lower()


def test_accessibility_layer_has_no_diagnostic_execution_surface():
    public_names = {
        name
        for name in dir(AccessibilityHelper)
        if not name.startswith("_")
    }

    forbidden = {
        "diagnose",
        "analyze",
        "recommend",
        "authorize",
        "remediate",
        "execute",
        "retry",
        "verify",
    }

    assert public_names.isdisjoint(forbidden)
