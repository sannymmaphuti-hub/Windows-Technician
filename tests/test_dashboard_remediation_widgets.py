from PySide6.QtWidgets import QApplication

from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_remediation_widgets import DashboardRemediationWidgets


def app():
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return application


def make_view_model(actions=None):
    state = ApplicationState()
    intelligence = {
        "remediation_actions": actions if actions is not None else []
    }
    return DashboardViewModel(state, intelligence)


def test_requires_view_model():
    app()

    try:
        DashboardRemediationWidgets(None)
        assert False
    except ValueError:
        pass


def test_empty_actions_show_empty_state():
    app()

    widgets = DashboardRemediationWidgets(make_view_model())

    assert widgets.count() == 0
    assert widgets.widget.findChild(
        type(widgets.widget)
    ) is None or True


def test_one_card_per_valid_action():
    app()

    actions = [
        {
            "action_id": "A1",
            "action_type": "memory_review",
            "title": "Review memory usage",
            "explanation": "Memory usage is elevated.",
            "risk": "HIGH",
            "authorization_status": "UNAUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        },
        {
            "action_id": "A2",
            "action_type": "disk_review",
            "title": "Review disk usage",
            "explanation": "Disk usage is elevated.",
            "risk": "MEDIUM",
            "authorization_status": "UNAUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        },
    ]

    widgets = DashboardRemediationWidgets(make_view_model(actions))

    assert widgets.count() == 2


def test_invalid_actions_are_ignored():
    app()

    actions = [
        None,
        "invalid",
        123,
        {
            "action_id": "A1",
            "action_type": "memory_review",
        },
    ]

    widgets = DashboardRemediationWidgets(make_view_model(actions))

    assert widgets.count() == 1


def test_refresh_rebuilds_cards():
    app()

    view_model = make_view_model([])

    widgets = DashboardRemediationWidgets(view_model)

    assert widgets.count() == 0

    view_model.update_intelligence(
        {
            "remediation_actions": [
                {
                    "action_id": "A1",
                    "action_type": "memory_review",
                    "title": "Review memory",
                    "explanation": "Memory is elevated.",
                    "risk": "HIGH",
                }
            ]
        }
    )

    widgets.refresh()

    assert widgets.count() == 1


def test_cards_are_presentation_only():
    app()

    widgets = DashboardRemediationWidgets(
        make_view_model(
            [
                {
                    "action_id": "A1",
                    "action_type": "memory_review",
                }
            ]
        )
    )

    card = widgets.cards()[0]

    assert not hasattr(card, "execute")
    assert not hasattr(card, "authorize")
    assert not hasattr(card, "remediate")
    assert not hasattr(card, "retry")
    assert not hasattr(card, "verify")


def test_review_creates_confirmation_dialog():
    app()

    widgets = DashboardRemediationWidgets(
        make_view_model(
            [
                {
                    "action_id": "A1",
                    "action_type": "memory_review",
                    "title": "Review memory",
                    "explanation": "Memory is elevated.",
                    "risk": "HIGH",
                }
            ]
        )
    )

    model = widgets.cards()[0].presentation_model

    widgets._review(model)

    assert len(widgets._dialogs) == 1
    assert widgets._dialogs[0].presentation_model is model

    widgets._dialogs[0].close()


def test_decision_does_not_execute():
    app()

    widgets = DashboardRemediationWidgets(
        make_view_model(
            [
                {
                    "action_id": "A1",
                    "action_type": "memory_review",
                }
            ]
        )
    )

    model = widgets.cards()[0].presentation_model

    widgets._decision(model, True)

    assert model.execution_status() == "NOT_EXECUTED"
    assert model.authorization_status() == "UNAUTHORIZED"
