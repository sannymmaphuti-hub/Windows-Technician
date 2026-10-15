from copy import deepcopy

from PySide6.QtCore import Signal

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QToolButton, QPlainTextEdit
from PySide6.QtWidgets import QSizePolicy

from engine.accessibility import AccessibilityHelper
from engine.keyboard_navigation import KeyboardNavigation

from engine.dashboard_diagnostic_cards import DashboardDiagnosticCards
from engine.dashboard_remediation_widgets import DashboardRemediationWidgets
from engine.accessibility import AccessibilityHelper
from engine.keyboard_navigation import KeyboardNavigation


class DashboardSection(QFrame):
    """
    Presentation section that preserves the historical dashboard
    label contract while exposing a readable text representation.

    The section does not diagnose, reason, recommend, authorize,
    remediate, execute, retry, or verify.
    """

    def __init__(self, title, object_name, parent=None, scrollable=False):
        super().__init__(parent)

        self.setObjectName(f"{object_name}Section")

        accessibility_names = {
            "dashboardHealthStatus": "System health status",
            "dashboardHealthScore": "System health score",
            "dashboardFindingCount": "Diagnostic finding count",
            "dashboardRelationshipCount": "System relationships",
            "dashboardRootCauseCount": "System root causes",
            "dashboardRecommendationCount": "System recommendations",
        }

        accessibility_name = accessibility_names.get(
            object_name,
            title,
        )

        AccessibilityHelper.describe(
            self,
            accessibility_name,
            f"{title} information displayed by the Windows Technician dashboard.",
        )

        self.title_label = QLabel(title)
        self.title_label.setObjectName(object_name)
        self.title_label.setWordWrap(True)

        if scrollable:
            self.value_label = QPlainTextEdit()
            self.value_label.setReadOnly(True)
            self.value_label.setLineWrapMode(
                QPlainTextEdit.LineWrapMode.WidgetWidth
            )
            self.value_label.setMinimumHeight(140)
            self.value_label.setMaximumHeight(220)
            self.value_label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )
        else:
            self.value_label = QLabel()
            self.value_label.setWordWrap(True)

        self.value_label.setObjectName(f"{object_name}Value")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def text(self):
        if isinstance(self.value_label, QPlainTextEdit):
            return self.value_label.toPlainText()
        return self.value_label.text()


class DashboardWidget(QFrame):
    diagnostics_requested = Signal()

    """
    Main presentation dashboard for Windows Technician.

    The dashboard displays existing intelligence and remediation
    decisions. It does not diagnose, reason, authorize, execute,
    retry, or verify remediation itself.
    """

    def __init__(self, view_model, parent=None):

        super().__init__(parent)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        if view_model is None:
            raise ValueError("view_model is required.")

        self.view_model = view_model
        self.setObjectName("dashboard")

        AccessibilityHelper.describe(
            self,
            "Windows Technician dashboard",
            "Dashboard presenting current system health, diagnostic findings, relationships, root causes, recommendations, and remediation actions.",
        )

        self._build_ui()
        self.refresh()
        self._configure_responsive_labels()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("Windows Technician Dashboard")
        self.title_label.setObjectName("dashboardTitle")

        AccessibilityHelper.describe(
            self.title_label,
            "Dashboard title",
            "Windows Technician Dashboard.",
        )
        self.title_label.setWordWrap(True)

        layout.addWidget(self.title_label)

        self.run_diagnostics_button = QToolButton()
        self.run_diagnostics_button.setText("Run Diagnostics")
        self.run_diagnostics_button.setObjectName("runDiagnosticsButton")
        self.run_diagnostics_button.setAccessibleName("Run Windows diagnostics")
        self.run_diagnostics_button.setToolTip(
            "Run the registered Windows diagnostic engines. "
            "This does not authorize or execute repairs."
        )
        self.run_diagnostics_button.clicked.connect(
            self.diagnostics_requested.emit
        )

        self.diagnostics_status_label = QLabel(
            "Ready to diagnose this computer."
        )
        self.diagnostics_status_label.setObjectName(
            "diagnosticsExecutionStatus"
        )
        self.diagnostics_status_label.setWordWrap(True)
        self.diagnostics_status_label.setAccessibleName(
            "Diagnostic execution status"
        )

        layout.addWidget(self.run_diagnostics_button)
        layout.addWidget(self.diagnostics_status_label)

        self.health_status_label = self._value_section(
            "Health",
            "dashboardHealthStatus",
        )

        # Historical compatibility surface.
        self.health_label = self._value_section(
            "Health Summary",
            "dashboardHealthSummary",
        )

        self.health_score_label = self._value_section(
            "Health Score",
            "dashboardHealthScore",
        )

        self.findings_label = self._value_section(
            "Findings",
            "dashboardFindingCount",
        )

        self.relationships_label = self._value_section(
            "Relationships",
            "dashboardRelationshipCount",
        )

        self.root_causes_label = self._value_section(
            "Root Causes",
            "dashboardRootCauseCount",
        )

        self.recommendations_label = self._value_section(
            "Recommendations",
            "dashboardRecommendationCount",
            scrollable=True,
        )

        self.diagnostic_cards = DashboardDiagnosticCards(
            self.view_model
        )

        self.diagnostic_container = QVBoxLayout()
        self.diagnostic_container.setContentsMargins(0, 0, 0, 0)
        self.diagnostic_container.setSpacing(10)

        self.no_findings_label = QLabel(
            "No diagnostic findings detected."
        )
        self.no_findings_label.setObjectName(
            "dashboardNoFindings"
        )
        self.no_findings_label.setWordWrap(True)

        layout.addWidget(self.health_status_label)
        layout.addWidget(self.health_score_label)
        layout.addWidget(self.findings_label)
        layout.addWidget(self.relationships_label)
        layout.addWidget(self.root_causes_label)
        layout.addWidget(self.recommendations_label)

        diagnostic_frame = QFrame()
        diagnostic_frame.setObjectName(
            "dashboardDiagnosticCards"
        )
        diagnostic_frame.setLayout(
            self.diagnostic_container
        )

        layout.addWidget(diagnostic_frame)

        self.remediation_widgets = DashboardRemediationWidgets(
            self.view_model,
            self,
        )

        layout.addWidget(self.remediation_widgets.widget)

        layout.addStretch()

    @staticmethod
    def _value_section(title, object_name, scrollable=False):
        return DashboardSection(
            title,
            object_name,
            scrollable=scrollable,
        )

    @staticmethod
    def _format_items(items):
        """
        Convert existing intelligence records into stable,
        human-readable dashboard text.

        This is presentation formatting only.
        """

        if items is None:
            return ""

        if not isinstance(items, list):
            items = [items]

        rendered = []

        for item in items:
            if isinstance(item, dict):
                parts = []

                for key, value in item.items():
                    if isinstance(value, (dict, list)):
                        value = str(value)

                    parts.append(
                        f"{key}: {value}"
                    )

                rendered.append(
                    " | ".join(parts)
                )

            else:
                rendered.append(str(item))

        return "\n".join(rendered)

    @staticmethod
    def _format_guidance_items(items):
        """
        Render structured system recommendations for dashboard users.

        This formats presentation data only. It does not modify
        recommendation evidence or authorize remediation.
        """
        if items is None:
            return ""

        if not isinstance(items, list):
            items = [items]

        rendered = []

        for index, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                rendered.append(f"{index}. {item}")
                continue

            priority = str(
                item.get("priority", "UNSPECIFIED")
            ).replace("_", " ").upper()

            domain = item.get("domain")
            if not domain:
                domains = item.get("domains")
                if isinstance(domains, (list, tuple, set)):
                    domain = ", ".join(
                        str(value) for value in domains
                    )
                elif domains:
                    domain = str(domains)

            action = item.get("action")
            rationale = item.get("rationale")
            recommendation_type = item.get("type")

            # Support recommendations that wrap the original finding.
            finding = item.get("finding")
            if isinstance(finding, dict):
                finding_type = (
                    finding.get("finding_type")
                    or finding.get("type")
                    or finding.get("category")
                )
                finding_severity = (
                    finding.get("severity")
                    or finding.get("level")
                )
            else:
                finding_type = None
                finding_severity = None

            lines = [
                f"{index}. [{priority}]"
            ]

            if domain:
                lines.append(f"   Domain: {domain}")

            if finding_type:
                lines.append(
                    "   Finding: "
                    + str(finding_type).replace("_", " ")
                )

            if finding_severity:
                lines.append(
                    "   Severity: "
                    + str(finding_severity).replace("_", " ").upper()
                )

            if recommendation_type == "SYSTEM_PATTERN":
                pattern = item.get("pattern")
                if pattern:
                    lines.append(f"   Pattern: {pattern}")

            if action:
                lines.append(f"   Recommended action: {action}")

            if rationale:
                lines.append(f"   Why: {rationale}")

            # Preserve useful text for legacy recommendation records.
            if not action and not rationale and not finding_type:
                for key in ("message", "description", "recommendation"):
                    value = item.get(key)
                    if isinstance(value, (str, int, float)) and value:
                        lines.append(f"   {key.capitalize()}: {value}")

            rendered.append("\n".join(lines))

        return "\n\n".join(rendered)

    def _clear_diagnostic_cards(self):
        while self.diagnostic_container.count():
            item = self.diagnostic_container.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _render_diagnostic_cards(self):
        self._clear_diagnostic_cards()

        models = self.diagnostic_cards.cards()

        if not models:
            self.diagnostic_container.addWidget(
                self.no_findings_label
            )
            return

        self.no_findings_label.setParent(None)

        from engine.diagnostic_card_widget import (
            DiagnosticCardWidget,
        )

        for model in models:
            card = DiagnosticCardWidget(
                model,
                self,
            )

            self.diagnostic_container.addWidget(card)

    def set_diagnostics_status(self, message):
        """Update user-visible execution feedback."""
        self.diagnostics_status_label.setText(str(message))

    def set_diagnostics_running(self, running):
        """Prevent overlapping diagnostic runs."""
        self.run_diagnostics_button.setEnabled(not running)
        self.run_diagnostics_button.setText(
            "Running Diagnostics..." if running else "Run Diagnostics"
        )

    def to_dict(self):
        return {
            "summary": deepcopy(
                self.view_model.summary()
            ),
            "diagnostic_card_count": (
                self.diagnostic_cards.count()
            ),
            "remediation_action_count": (
                self.remediation_widgets.count()
            ),
        }

    def _configure_responsive_labels(self):
        for label in self.findChildren(QLabel):
            label.setWordWrap(True)
            label.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
            )

    def refresh(self):
        summary = self.view_model.summary()

        status = str(summary["status"])
        score = summary["health_score"]

        score_text = (
            "N/A"
            if score is None
            else str(score)
        )

        self.health_status_label.value_label.setText(
            status
        )

        AccessibilityHelper.set_dynamic_description(
            self.health_status_label,
            (
                f"Current system health status is {status}. "
                f"Health score is {score_text}."
            ),
        )

        self.health_score_label.value_label.setText(
            score_text
        )

        AccessibilityHelper.set_dynamic_description(
            self.health_score_label,
            f"Current system health score is {score_text}.",
        )

        self.health_label.value_label.setText(
            f"{status} | Score: {score_text}"
        )

        AccessibilityHelper.set_dynamic_description(
            self.health_label,
            (
                f"Health summary: status {status}, "
                f"score {score_text}."
            ),
        )

        finding_count = summary["finding_count"]

        self.findings_label.value_label.setText(
            str(finding_count)
        )

        AccessibilityHelper.set_dynamic_description(
            self.findings_label,
            (
                f"There are {finding_count} "
                f"diagnostic findings."
            ),
        )

        relationships = self.view_model.relationships()
        root_causes = self.view_model.root_causes()
        recommendations = self.view_model.recommendations()

        self.relationships_label.value_label.setText(
            self._format_items(relationships)
            if relationships
            else "No relationships identified from current evidence."
        )

        self.root_causes_label.value_label.setText(
            self._format_items(root_causes)
            if root_causes
            else "No root causes established from current evidence."
        )

        self.recommendations_label.value_label.setPlainText(
            self._format_guidance_items(recommendations)
            if recommendations
            else "No recommendations available."
        )

        AccessibilityHelper.set_dynamic_description(
            self.relationships_label,
            f"There are {len(relationships)} system relationships."
        )

        AccessibilityHelper.set_dynamic_description(
            self.root_causes_label,
            f"There are {len(root_causes)} identified root causes."
        )

        AccessibilityHelper.set_dynamic_description(
            self.recommendations_label,
            f"There are {len(recommendations)} system recommendations."
        )

        self.diagnostic_cards.refresh()
        self._render_diagnostic_cards()
        self.remediation_widgets.refresh()

        review_buttons = [
            card.review_button
            for card in self.remediation_widgets.cards()
            if card.review_button.isEnabled()
        ]

        from engine.keyboard_navigation import KeyboardNavigation

        KeyboardNavigation.set_tab_order(
            review_buttons
        )
