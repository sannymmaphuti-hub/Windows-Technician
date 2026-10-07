from copy import deepcopy

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from engine.dashboard_diagnostic_cards import DashboardDiagnosticCards
from engine.dashboard_remediation_widgets import DashboardRemediationWidgets
from engine.accessibility import AccessibilityHelper


class DashboardSection(QFrame):
    """
    Presentation section that exposes readable and accessible
    dashboard state.

    This section does not diagnose, reason, recommend, authorize,
    remediate, execute, retry, or verify.
    """

    def __init__(self, title, object_name, parent=None):
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

        self.value_label = QLabel()
        self.value_label.setObjectName(f"{object_name}Value")
        self.value_label.setWordWrap(True)

        AccessibilityHelper.describe(
            self.title_label,
            accessibility_name,
            f"{title} displayed by the Windows Technician dashboard.",
        )

        AccessibilityHelper.describe(
            self.value_label,
            accessibility_name,
            f"Current {title.lower()} displayed by the Windows Technician dashboard.",
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def text(self):
        return self.value_label.text()

    def set_accessible_value(self, value_description):
        AccessibilityHelper.set_dynamic_description(
            self.value_label,
            value_description,
        )
