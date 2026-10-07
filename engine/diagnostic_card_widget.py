from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
)

from engine.accessibility import AccessibilityHelper


class DiagnosticCardWidget(QFrame):
    """
    Presentation-only widget for one DiagnosticCardModel.

    The widget renders an existing diagnostic finding. It does
    not diagnose, reason, recommend, authorize, remediate, or
    execute anything.
    """

    def __init__(self, card_model, parent=None):
        super().__init__(parent)

        if card_model is None:
            raise ValueError("card_model is required.")

        self.card_model = card_model

        self.setObjectName("diagnosticCard")

        AccessibilityHelper.describe(
            self,
            "Diagnostic finding",
            "A diagnostic finding identified by Windows Technician.",
        )

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.severity_label = QLabel()
        self.severity_label.setObjectName("diagnosticSeverity")

        AccessibilityHelper.describe(
            self.severity_label,
            "Diagnostic severity",
            "Severity assigned to this diagnostic finding.",
        )

        self.category_label = QLabel()
        self.category_label.setObjectName("diagnosticCategory")

        AccessibilityHelper.describe(
            self.category_label,
            "Diagnostic category",
            "System category associated with this finding.",
        )

        self.title_label = QLabel()
        self.title_label.setObjectName("diagnosticTitle")
        self.title_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.title_label,
            "Diagnostic finding title",
            "Title identifying the diagnostic finding.",
        )

        self.explanation_label = QLabel()
        self.explanation_label.setObjectName("diagnosticExplanation")
        self.explanation_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.explanation_label,
            "Diagnostic explanation",
            "Explanation of what the finding means.",
        )

        self.evidence_label = QLabel()
        self.evidence_label.setObjectName("diagnosticEvidence")
        self.evidence_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.evidence_label,
            "Diagnostic evidence",
            "Evidence supporting the diagnostic finding.",
        )

        self.next_step_label = QLabel()
        self.next_step_label.setObjectName("diagnosticNextStep")
        self.next_step_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.next_step_label,
            "Diagnostic next step",
            "Suggested next step associated with this finding.",
        )

        layout.addWidget(self.severity_label)
        layout.addWidget(self.category_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.explanation_label)
        layout.addWidget(self.evidence_label)
        layout.addWidget(self.next_step_label)

    @staticmethod
    def _format_evidence(evidence):
        if not evidence:
            return "Evidence: No evidence available."

        lines = ["Evidence:"]

        for item in evidence:
            if isinstance(item, dict):
                parts = [
                    f"{key}: {value}"
                    for key, value in item.items()
                ]
                lines.append("• " + ", ".join(parts))
            else:
                lines.append(f"• {item}")

        return "\n".join(lines)

    def refresh(self):
        severity = self.card_model.severity()
        category = self.card_model.category()
        title = self.card_model.title()
        explanation = self.card_model.explanation()
        evidence = self.card_model.evidence()
        next_step = self.card_model.next_step()

        self.severity_label.setText(
            f"Severity: {severity}"
        )

        self.category_label.setText(
            f"Category: {category}"
        )

        self.title_label.setText(title)
        self.explanation_label.setText(explanation)

        self.evidence_label.setText(
            self._format_evidence(evidence)
        )

        self.next_step_label.setText(
            f"Next step: {next_step}"
        )

        AccessibilityHelper.set_state(
            self,
            "Diagnostic finding",
            (
                f"Diagnostic finding: {severity} severity "
                f"{category} finding: {title}. "
                f"{explanation} "
                f"Next step: {next_step}."
            ),
        )

        AccessibilityHelper.set_dynamic_description(
            self.severity_label,
            f"Diagnostic severity is {severity}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.category_label,
            f"Diagnostic category is {category}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.title_label,
            f"Diagnostic finding title: {title}.",
        )

        AccessibilityHelper.set_dynamic_description(
            self.explanation_label,
            f"Diagnostic explanation: {explanation}",
        )

        AccessibilityHelper.set_dynamic_description(
            self.evidence_label,
            self._format_evidence(evidence),
        )

        AccessibilityHelper.set_dynamic_description(
            self.next_step_label,
            f"Suggested next step: {next_step}",
        )
