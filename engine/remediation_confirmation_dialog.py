from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from engine.accessibility import AccessibilityHelper


class RemediationConfirmationDialog(QDialog):
    """
    Presentation-only confirmation dialog for an existing
    remediation presentation model.

    The dialog records the user's approval decision through a
    signal.
    It does not authorize, execute, retry, or verify remediation.
    """

    decision_made = Signal(object, bool)

    def __init__(self, presentation_model, parent=None):
        super().__init__(parent)

        if presentation_model is None:
            raise ValueError("presentation_model is required.")

        self.presentation_model = presentation_model

        self.setObjectName(
            "remediationConfirmationDialog"
        )
        self.setWindowTitle("Review Remediation")

        AccessibilityHelper.describe(
            self,
            "Remediation confirmation",
            (
                "Review a proposed remediation action "
                "before the user's decision."
            ),
        )

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setObjectName(
            "confirmationTitle"
        )

        AccessibilityHelper.describe(
            self.title_label,
            "Confirmation title",
            "Title of the remediation confirmation.",
        )

        self.explanation_label = QLabel()
        self.explanation_label.setObjectName(
            "confirmationExplanation"
        )

        AccessibilityHelper.describe(
            self.explanation_label,
            "Confirmation explanation",
            "Explanation of the proposed remediation.",
        )

        self.risk_label = QLabel()
        self.risk_label.setObjectName(
            "confirmationRisk"
        )

        AccessibilityHelper.describe(
            self.risk_label,
            "Confirmation risk",
            "Risk level of the proposed remediation.",
        )

        self.authorization_label = QLabel()
        self.authorization_label.setObjectName(
            "confirmationAuthorization"
        )

        AccessibilityHelper.describe(
            self.authorization_label,
            "Current authorization status",
            "Current authorization state before the user's decision.",
        )

        self.action_label = QLabel()
        self.action_label.setObjectName(
            "confirmationAction"
        )

        AccessibilityHelper.describe(
            self.action_label,
            "Proposed remediation action",
            "The remediation action that is being presented for review.",
        )

        self.warning_label = QLabel()
        self.warning_label.setObjectName(
            "confirmationWarning"
        )

        AccessibilityHelper.describe(
            self.warning_label,
            "Remediation approval warning",
            (
                "Approval records the user's decision. "
                "The existing remediation workflow remains "
                "responsible for authorization, execution, "
                "and verification."
            ),
        )

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.setObjectName(
            "confirmationButtons"
        )

        approve = self.buttons.button(
            QDialogButtonBox.StandardButton.Ok
        )

        cancel = self.buttons.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        approve.setText("Approve")
        cancel.setText("Cancel")

        AccessibilityHelper.describe_and_focus(
            approve,
            "Approve remediation",
            (
                "Approve the proposed remediation. "
                "This records the user's decision."
            ),
        )

        AccessibilityHelper.describe_and_focus(
            cancel,
            "Cancel remediation",
            (
                "Cancel the remediation review without "
                "approving the proposed action."
            ),
        )

        self.buttons.accepted.connect(
            self._approve
        )

        self.buttons.rejected.connect(
            self._cancel
        )

        layout.addWidget(self.title_label)
        layout.addWidget(self.explanation_label)
        layout.addWidget(self.risk_label)
        layout.addWidget(self.authorization_label)
        layout.addWidget(self.action_label)
        layout.addWidget(self.warning_label)
        layout.addWidget(self.buttons)

    def refresh(self):
        model = self.presentation_model

        title = model.title()
        explanation = model.explanation()
        risk = model.risk()
        authorization = model.authorization_status()
        action_type = model.action_type()

        self.title_label.setText(title)

        self.explanation_label.setText(
            explanation
        )

        self.risk_label.setText(
            f"Risk: {risk}"
        )

        self.authorization_label.setText(
            f"Current authorization: {authorization}"
        )

        self.action_label.setText(
            f"Proposed action: {action_type}"
        )

        self.warning_label.setText(
            (
                "Approval records the user's decision. "
                "The existing remediation workflow remains "
                "responsible for authorization, execution, "
                "and verification."
            )
        )

        AccessibilityHelper.set_state(
            self,
            "Remediation confirmation",
            (
                f"Reviewing {title}. "
                f"Proposed remediation action: {action_type}. "
                f"Current authorization: {authorization}. "
                f"Risk: {risk}. "
                "Approval records the user's decision. "
                "The existing remediation workflow remains "
                "responsible for authorization, execution, "
                "and verification."
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.title_label,
            f"Confirmation title: {title}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.explanation_label,
            (
                f"Confirmation explanation: "
                f"{explanation}"
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.risk_label,
            f"Confirmation risk level is {risk}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.authorization_label,
            (
                "Current authorization status is "
                f"{authorization}."
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.action_label,
            (
                "Proposed remediation action is "
                f"{action_type}."
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.warning_label,
            (
                "Approval records the user's decision. "
                "The existing remediation workflow remains "
                "responsible for authorization, execution, "
                "and verification."
            ),
        )

    def _approve(self):
        self.decision_made.emit(
            self.presentation_model,
            True,
        )
        self.accept()

    def _cancel(self):
        self.decision_made.emit(
            self.presentation_model,
            False,
        )
        self.reject()
