from PySide6.QtWidgets import QVBoxLayout, QLabel

from engine.remediation_action_card_widget import RemediationActionCardWidget
from engine.remediation_confirmation_dialog import RemediationConfirmationDialog


class DashboardRemediationWidgets:
    """
    Presentation integration for remediation actions on the dashboard.

    This component displays existing remediation actions and routes
    review decisions through the presentation layer.

    It does not authorize, execute, retry, verify, or modify
    remediation state.
    """

    def __init__(self, dashboard_view_model, parent=None):
        if dashboard_view_model is None:
            raise ValueError("dashboard_view_model is required.")

        self.dashboard_view_model = dashboard_view_model
        self.parent = parent
        self._cards = []
        self._dialogs = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.container = parent = self.parent

        self.widget = QLabel()
        self.widget.setObjectName("dashboardRemediationContainer")

        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)

    def _clear(self):
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()

        self._cards = []

        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def refresh(self):
        self._clear()

        intelligence = self.dashboard_view_model.intelligence
        actions = intelligence.get("remediation_actions")

        if not isinstance(actions, list):
            actions = []

        valid_actions = [
            action for action in actions
            if isinstance(action, dict)
        ]

        if not valid_actions:
            empty = QLabel("No remediation actions available.")
            empty.setObjectName("dashboardNoRemediationActions")
            empty.setWordWrap(True)
            self.layout.addWidget(empty)
            return

        for action in valid_actions:
            from engine.remediation_presentation_model import (
                RemediationPresentationModel,
            )

            model = RemediationPresentationModel(action)
            card = RemediationActionCardWidget(model, self.widget)
            card.review_requested.connect(self._review)
            self.layout.addWidget(card)
            self._cards.append(card)

        self.layout.addStretch()

    def _review(self, presentation_model):
        dialog = RemediationConfirmationDialog(
            presentation_model,
            self.widget,
        )

        dialog.decision_made.connect(self._decision)
        self._dialogs.append(dialog)

        dialog.show()

    def _decision(self, presentation_model, approved):
        # Deliberately presentation-only.
        # The existing remediation workflow owns authorization
        # and execution. This layer only exposes the user's decision.
        return None

    def cards(self):
        return list(self._cards)

    def count(self):
        return len(self._cards)
