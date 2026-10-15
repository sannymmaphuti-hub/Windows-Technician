from PySide6.QtWidgets import QSizePolicy, QLabel, QPushButton

from engine.main_window import MainWindow


def make_state():
    class State:
        status = "READY"
        active_case_id = None
        active_machine_id = None

        def to_dict(self):
            return {
                "application_name": "Windows Technician",
                "version": "1.0.0",
                "status": "READY",
                "active_case_id": None,
                "active_machine_id": None,
            }

    return State()


def test_main_window_has_responsive_minimum_size(qapp):
    window = MainWindow(make_state())

    minimum = window.minimumSize()

    assert minimum.width() >= 640
    assert minimum.height() >= 480


def test_main_window_is_resizable(qapp):
    window = MainWindow(make_state())

    assert window.sizePolicy().horizontalPolicy() == (
        QSizePolicy.Policy.Preferred
    )
    assert window.sizePolicy().verticalPolicy() == (
        QSizePolicy.Policy.Preferred
    )


def test_dashboard_expands_with_available_space(qapp):
    window = MainWindow(make_state())

    policy = window.dashboard.sizePolicy()

    assert policy.horizontalPolicy() == QSizePolicy.Policy.Expanding
    assert policy.verticalPolicy() == QSizePolicy.Policy.Expanding


def test_dashboard_diagnostic_cards_are_responsive(qapp):
    window = MainWindow(make_state())

    for card in window.dashboard.diagnostic_cards.cards():
        policy = card.sizePolicy()

        assert policy.horizontalPolicy() in (
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )


def test_dashboard_remediation_cards_are_responsive(qapp):
    window = MainWindow(make_state())

    for card in window.dashboard.remediation_widgets.cards():
        policy = card.sizePolicy()

        assert policy.horizontalPolicy() in (
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )


def test_window_can_resize_to_supported_minimum(qapp):
    window = MainWindow(make_state())

    window.resize(800, 600)
    window.show()
    qapp.processEvents()

    assert window.width() >= 640
    assert window.height() >= 480


def test_dashboard_text_widgets_support_wrapping(qapp):
    window = MainWindow(make_state())

    labels = window.dashboard.findChildren(QLabel)

    assert labels

    for label in labels:
        assert label.wordWrap()


def test_dashboard_interactive_controls_remain_reachable(qapp):
    window = MainWindow(make_state())

    buttons = window.dashboard.findChildren(QPushButton)

    for button in buttons:
        assert button.isEnabled()


def test_responsive_ui_is_presentation_only():
    source = open(
        "engine/main_window.py",
        encoding="utf-8",
    ).read()

    forbidden = (
        "diagnose(",
        "analyze(",
        "recommend(",
        "authorize(",
        "execute(",
        "remediate(",
        "retry(",
        "verify(",
    )

    for operation in forbidden:
        assert operation not in source
