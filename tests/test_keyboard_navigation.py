import pytest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QWidget,
)

from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_widget import DashboardWidget
from engine.keyboard_navigation import KeyboardNavigation
from engine.main_window import MainWindow
from engine.remediation_confirmation_dialog import (
    RemediationConfirmationDialog,
)
from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)


@pytest.fixture
def qapp():
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


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
            "system_findings": [],
            "remediation_actions": [
                {
                    "action_id": "A-001",
                    "action_type": "memory_review",
                    "title": "Review memory usage",
                    "explanation": "Memory pressure should be reviewed.",
                    "risk": "LOW",
                    "authorization_status": "UNAUTHORIZED",
                    "execution_status": "NOT_EXECUTED",
                },
                {
                    "action_id": "A-002",
                    "action_type": "disk_review",
                    "title": "Review disk usage",
                    "explanation": "Disk usage should be reviewed.",
                    "risk": "LOW",
                    "authorization_status": "UNAUTHORIZED",
                    "execution_status": "NOT_EXECUTED",
                },
            ],
        },
    )

    return DashboardWidget(view_model)


def test_navigation_requires_root():
    with pytest.raises(ValueError):
        KeyboardNavigation.interactive_widgets(None)


def test_set_tab_order_requires_widgets():
    with pytest.raises(ValueError):
        KeyboardNavigation.set_tab_order(None)


def test_set_tab_order_accepts_empty_collection(qapp):
    assert KeyboardNavigation.set_tab_order([]) == 0


def test_set_tab_order_rejects_none_entries(qapp):
    first = QPushButton()
    second = None

    with pytest.raises(ValueError):
        KeyboardNavigation.set_tab_order(
            [first, second]
        )


def test_set_tab_order_creates_sequential_focus_chain(qapp):
    root = QWidget()

    first = QPushButton("First", root)
    second = QPushButton("Second", root)
    third = QPushButton("Third", root)

    first.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    second.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    third.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    count = KeyboardNavigation.set_tab_order(
        [first, second, third]
    )

    assert count == 2

    first.show()
    second.show()
    third.show()

    root.show()
    root.activateWindow()
    root.raise_()
    qapp.processEvents()

    first.setFocus()
    qapp.processEvents()

    assert first.hasFocus()

    qapp.processEvents()

    assert second.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert third.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_interactive_widgets_excludes_non_focusable_labels(qapp):
    root = QWidget()

    label = QLabel("Information", root)
    button = QPushButton("Review", root)

    label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    widgets = KeyboardNavigation.interactive_widgets(root)

    assert button in widgets
    assert label not in widgets


def test_interactive_widgets_excludes_disabled_controls(qapp):
    root = QWidget()

    enabled = QPushButton("Enabled", root)
    disabled = QPushButton("Disabled", root)

    enabled.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    disabled.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    disabled.setEnabled(False)

    widgets = KeyboardNavigation.interactive_widgets(root)

    assert enabled in widgets
    assert disabled not in widgets


def test_focus_first_returns_first_enabled_widget(qapp):
    root = QWidget()

    first = QPushButton("First", root)
    second = QPushButton("Second", root)

    first.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    second.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    first.setEnabled(False)

    root.show()

    result = KeyboardNavigation.focus_first(
        [first, second]
    )

    qapp.processEvents()

    assert result is second
    assert second.hasFocus()


def test_focus_first_returns_none_for_empty_collection(qapp):
    assert KeyboardNavigation.focus_first([]) is None


def test_configure_discovers_interactive_widgets(qapp):
    root = QWidget()

    label = QLabel("Information", root)
    button = QPushButton("Review", root)

    label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    widgets = KeyboardNavigation.configure(root)

    assert button in widgets
    assert label not in widgets


def test_dashboard_remediation_buttons_are_keyboard_focusable(qapp):
    dashboard = make_dashboard()

    buttons = [
        card.review_button
        for card in dashboard.remediation_widgets.cards()
    ]

    assert len(buttons) == 2

    for button in buttons:
        assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert button.isEnabled()


def test_dashboard_remediation_buttons_have_deterministic_order(qapp):
    dashboard = make_dashboard()

    buttons = [
        card.review_button
        for card in dashboard.remediation_widgets.cards()
    ]

    assert buttons[0].accessibleName() == "Review remediation"
    assert buttons[1].accessibleName() == "Review remediation"

    KeyboardNavigation.set_tab_order(buttons)

    assert buttons[0].focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert buttons[1].focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_main_window_can_configure_keyboard_navigation(qapp):
    window = MainWindow(
        ApplicationState()
    )

    widgets = KeyboardNavigation.configure(window)

    assert isinstance(widgets, list)


def test_main_window_dashboard_has_keyboard_review_controls(qapp):
    window = MainWindow(
        ApplicationState()
    )

    window.dashboard_view_model.update_intelligence(
        {
            "health": {
                "status": "WARNING",
                "score": 74,
            },
            "system_findings": [],
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
        }
    )

    window.refresh_dashboard()

    buttons = window.dashboard.findChildren(
        QPushButton
    )

    assert len(buttons) == 1
    assert buttons[0].focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_confirmation_dialog_approve_and_cancel_are_focusable(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    approve = dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    )
    cancel = dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    )

    assert approve.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert cancel.focusPolicy() == Qt.FocusPolicy.StrongFocus


def test_confirmation_dialog_approve_remains_a_presentation_signal(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    decisions = []

    dialog.decision_made.connect(
        lambda model, approved: decisions.append(
            (model, approved)
        )
    )

    approve = dialog.buttons.button(
        dialog.buttons.StandardButton.Ok
    )

    approve.click()

    assert len(decisions) == 1
    assert decisions[0][1] is True


def test_confirmation_dialog_cancel_remains_a_presentation_signal(qapp):
    dialog = RemediationConfirmationDialog(
        make_remediation_model()
    )

    decisions = []

    dialog.decision_made.connect(
        lambda model, approved: decisions.append(
            (model, approved)
        )
    )

    cancel = dialog.buttons.button(
        dialog.buttons.StandardButton.Cancel
    )

    cancel.click()

    assert len(decisions) == 1
    assert decisions[0][1] is False


def test_keyboard_navigation_has_no_remediation_execution_surface():
    public_names = {
        name
        for name in dir(KeyboardNavigation)
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



