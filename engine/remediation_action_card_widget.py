from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from engine.accessibility import AccessibilityHelper


class RemediationActionCardWidget(QFrame):
    """
    Presentation-only widget for one remediation action.

    The widget displays an existing remediation action and emits a
    review request when the user chooses to inspect it.

    It does not authorize, execute, retry, verify, or modify
    remediation state.
    """

    review_requested = Signal(object)

    def __init__(self, presentation_model, parent=None):
        super().__init__(parent)

        if presentation_model is None:
            raise ValueError("presentation_model is required.")

        self.presentation_model = presentation_model

        self.setObjectName("remediationActionCard")

        AccessibilityHelper.describe(
            self,
            "Remediation action",
            "An existing remediation action that can be reviewed before approval.",
        )

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setObjectName("remediationTitle")
        self.title_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.title_label,
            "Remediation title",
            "Title of the proposed remediation.",
        )

        self.action_type_label = QLabel()
        self.action_type_label.setObjectName("remediationActionType")

        AccessibilityHelper.describe(
            self.action_type_label,
            "Remediation action type",
            "Type of remediation represented by this action.",
        )

        self.explanation_label = QLabel()
        self.explanation_label.setObjectName("remediationExplanation")
        self.explanation_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.explanation_label,
            "Remediation explanation",
            "Explanation of why the remediation is being proposed.",
        )

        self.risk_label = QLabel()
        self.risk_label.setObjectName("remediationRisk")

        AccessibilityHelper.describe(
            self.risk_label,
            "Remediation risk",
            "Risk level associated with the proposed remediation.",
        )

        self.authorization_label = QLabel()
        self.authorization_label.setObjectName("remediationAuthorization")

        AccessibilityHelper.describe(
            self.authorization_label,
            "Remediation authorization status",
            "Current authorization state of the remediation action.",
        )

        self.execution_label = QLabel()
        self.execution_label.setObjectName("remediationExecution")

        AccessibilityHelper.describe(
            self.execution_label,
            "Remediation execution status",
            "Current execution state of the remediation action.",
        )

        self.message_label = QLabel()
        self.message_label.setObjectName("remediationMessage")
        self.message_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.message_label,
            "Remediation status message",
            "Human-readable status message for the remediation action.",
        )

        self.review_button = QPushButton("Review")
        self.review_button.setObjectName("remediationReviewButton")

        AccessibilityHelper.describe_and_focus(
            self.review_button,
            "Review remediation",
            "Review the proposed remediation before making an approval decision.",
        )

        self.review_button.clicked.connect(
            self._request_review
        )

        layout.addWidget(self.title_label)
        layout.addWidget(self.action_type_label)
        layout.addWidget(self.explanation_label)
        layout.addWidget(self.risk_label)
        layout.addWidget(self.authorization_label)
        layout.addWidget(self.execution_label)
        layout.addWidget(self.message_label)
        layout.addWidget(self.review_button)

    def _request_review(self):
        self.review_requested.emit(
            self.presentation_model
        )

    def refresh(self):
        model = self.presentation_model

        authorization = model.authorization_status()
        execution = model.execution_status()
        risk = model.risk()
        title = model.title()

        self.title_label.setText(title)

        self.action_type_label.setText(
            f"Action: {model.action_type()}"
        )

        self.explanation_label.setText(
            model.explanation()
        )

        self.risk_label.setText(
            f"Risk: {risk}"
        )

        self.authorization_label.setText(
            f"Authorization: {authorization}"
        )

        self.execution_label.setText(
            f"Execution: {execution}"
        )

        self.message_label.setText(
            model.user_message()
        )

        self.review_button.setEnabled(
            not model.has_executed()
        )

        AccessibilityHelper.set_state(
            self,
            "Remediation action",
            (
                f"{title}. "
                f"Risk: {risk}. "
                f"Authorization: {authorization}. "
                f"Execution: {execution}. "
                f"{model.user_message()}"
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.authorization_label,
            f"Remediation authorization status is {authorization}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.execution_label,
            f"Remediation execution status is {execution}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.review_button,
            (
                f"Review proposed remediation: {title}. "
                f"Authorization is {authorization}. "
                f"Execution is {execution}."
            ),
        )
