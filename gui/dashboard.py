from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from gui.diagnostic_card import DiagnosticCard
from gui.diagnostic_worker import DiagnosticWorker
from gui.metric_card import MetricCard


class DashboardWidget(QWidget):
    def __init__(self, technician_app):
        super().__init__()

        self.technician_app = technician_app
        self.view_model = None

        # Diagnostic Thread State
        self._diagnostic_thread = None
        self._diagnostic_worker = None

        # Dashboard Window
        self.setMinimumSize(900, 650)

        # Header
        self.header = QFrame()
        self.header.setObjectName("DashboardHeader")
        self.header.setStyleSheet(
            """
            QFrame#DashboardHeader {
                border-radius: 12px;
                padding: 16px;
            }
            """
        )

        self.title = QLabel("System Overview")

        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        self.title.setFont(title_font)

        self.execution_status = QLabel("Ready")

        execution_font = QFont()
        execution_font.setPointSize(10)
        execution_font.setBold(True)
        self.execution_status.setFont(execution_font)

        self.execution_state = "READY"
        self.execution_label = "Ready"
        self.execution_severity = "info"

        # Run Diagnostics Button
        self.run_diagnostics_button = QPushButton(
            "Run Diagnostics"
        )

        self.run_diagnostics_button.clicked.connect(
            self._run_diagnostics
        )

        header_layout = QVBoxLayout()
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.execution_status)
        header_layout.addWidget(
            self.run_diagnostics_button
        )

        self.header.setLayout(header_layout)

        # Health Summary
        self.health_summary = QFrame()
        self.health_summary.setObjectName("HealthSummary")
        self.health_summary.setStyleSheet(
            """
            QFrame#HealthSummary {
                border-radius: 12px;
                padding: 16px;
            }
            """
        )

        self.health_status = QLabel("Unknown")

        health_font = QFont()
        health_font.setPointSize(24)
        health_font.setBold(True)
        self.health_status.setFont(health_font)

        self.health_severity = "info"

        health_layout = QVBoxLayout()
        health_layout.addWidget(self.health_status)

        self.health_summary.setLayout(health_layout)

        # Metric Cards
        self.cpu_card = MetricCard(
            title="CPU",
            value="N/A",
            status="Unknown",
            detail="Usage unavailable",
        )

        self.memory_card = MetricCard(
            title="Memory",
            value="N/A",
            status="Unknown",
            detail="Usage unavailable",
        )

        self.storage_card = MetricCard(
            title="Storage",
            value="N/A",
            status="Unknown",
            detail="Storage unavailable",
        )

        # Legacy / Presentation References
        self.cpu_usage = self.cpu_card.value
        self.memory_usage = self.memory_card.value
        self.storage_usage = self.storage_card.value

        self.storage_capacity = QLabel("N/A")
        self.storage_free = QLabel("N/A")

        self.storage_capacity.setVisible(False)
        self.storage_free.setVisible(False)

        # Horizontal Metric Layout
        metrics_layout = QHBoxLayout()
        metrics_layout.addWidget(self.cpu_card, 1)
        metrics_layout.addWidget(self.memory_card, 1)
        metrics_layout.addWidget(self.storage_card, 1)

        # Diagnostic Cards
        self.diagnostic_insight_card = DiagnosticCard(
            title="Diagnostic Insight",
            content="No diagnostic insight available.",
            severity="info",
        )

        self.root_cause_card = DiagnosticCard(
            title="Root Cause",
            content="No primary root cause identified.",
            severity="info",
        )

        self.recommendation_card = DiagnosticCard(
            title="Recommendation",
            content="No recommendation available.",
            severity="info",
        )

        # Existing Dashboard References
        self.primary_insight = (
            self.diagnostic_insight_card.content
        )

        self.primary_root_cause = (
            self.root_cause_card.content
        )

        self.primary_recommendation = (
            self.recommendation_card.content
        )

        # Diagnostic Typography
        insight_font = QFont()
        insight_font.setPointSize(14)
        insight_font.setBold(True)
        self.diagnostic_insight_card.content.setFont(
            insight_font
        )

        root_cause_font = QFont()
        root_cause_font.setPointSize(11)
        root_cause_font.setBold(True)
        self.root_cause_card.content.setFont(
            root_cause_font
        )

        recommendation_font = QFont()
        recommendation_font.setPointSize(11)
        recommendation_font.setBold(True)
        self.recommendation_card.content.setFont(
            recommendation_font
        )

        # Diagnostic Content Area
        self.content_area = QFrame()
        self.content_area.setObjectName("DiagnosticContent")

        self.content_area.setStyleSheet(
            """
            QFrame#DiagnosticContent {
                border-radius: 12px;
                padding: 8px;
            }
            """
        )

        # Scroll area for diagnostic cards
        self.diagnostic_scroll = QScrollArea()
        self.diagnostic_scroll.setWidgetResizable(True)
        self.diagnostic_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.diagnostic_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.diagnostic_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        # Container inside the scroll area
        diagnostic_container = QWidget()

        content_layout = QVBoxLayout(
            diagnostic_container
        )

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        content_layout.setSpacing(12)

        content_layout.addWidget(
            self.diagnostic_insight_card
        )

        content_layout.addWidget(
            self.root_cause_card
        )

        content_layout.addWidget(
            self.recommendation_card
        )

        # Keep cards at their natural height
        content_layout.addStretch()

        self.diagnostic_scroll.setWidget(
            diagnostic_container
        )

        # Put the scroll area inside the dashboard content frame
        content_area_layout = QVBoxLayout(
            self.content_area
        )

        content_area_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        content_area_layout.addWidget(
            self.diagnostic_scroll
        )

        # Main Dashboard Layout
        main_layout = QVBoxLayout()

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.health_summary)
        main_layout.addLayout(metrics_layout)
        main_layout.addWidget(self.content_area)

        self.setLayout(main_layout)

    # --------------------------------------------------------------
    # Run Diagnostics
    # --------------------------------------------------------------

    def _run_diagnostics(self):
        if self._diagnostic_thread is not None:
            if self._diagnostic_thread.isRunning():
                return

        self._set_execution_state(
            state="RUNNING",
            label="Analyzing...",
            severity="info",
        )

        self.run_diagnostics_button.setEnabled(False)

        self._diagnostic_thread = QThread()

        self._diagnostic_worker = DiagnosticWorker(
            self.technician_app
        )

        self._diagnostic_worker.moveToThread(
            self._diagnostic_thread
        )

        self._diagnostic_thread.started.connect(
            self._diagnostic_worker.run
        )

        self._diagnostic_worker.finished.connect(
            self._on_diagnostics_finished
        )

        self._diagnostic_worker.error.connect(
            self._on_diagnostics_error
        )

        self._diagnostic_worker.finished.connect(
            self._diagnostic_thread.quit,
            Qt.DirectConnection,
        )

        self._diagnostic_worker.error.connect(
            self._diagnostic_thread.quit,
            Qt.DirectConnection,
        )

        self._diagnostic_worker.finished.connect(
            self._diagnostic_worker.deleteLater
        )

        self._diagnostic_worker.error.connect(
            self._diagnostic_worker.deleteLater
        )

        self._diagnostic_thread.finished.connect(
            self._on_diagnostic_thread_finished
        )

        self._diagnostic_thread.start()

    def _on_diagnostics_finished(self):
        view_model = (
            self.technician_app.get_dashboard_view_model()
        )

        self.set_view_model(view_model)

        self.run_diagnostics_button.setEnabled(True)

    def _on_diagnostics_error(self, message):
        self._set_execution_state(
            state="ERROR",
            label="Diagnostic Failed",
            severity="critical",
        )

        self.run_diagnostics_button.setEnabled(True)

    def _on_diagnostic_thread_finished(self):
        thread = self._diagnostic_thread

        self._diagnostic_worker = None
        self._diagnostic_thread = None

        if thread is not None:
            thread.deleteLater()

    def _set_execution_state(
        self,
        state,
        label,
        severity,
    ):
        self.execution_state = state
        self.execution_label = label
        self.execution_severity = severity

        self.execution_status.setText(
            label
        )

    # --------------------------------------------------------------
    # View Model
    # --------------------------------------------------------------

    def set_view_model(self, view_model):
        self.view_model = view_model

        # Execution State
        self.execution_state = view_model.execution_state
        self.execution_label = view_model.execution_label
        self.execution_severity = view_model.execution_severity

        self.execution_status.setText(
            self.execution_label
        )

        # Health State
        self.health_severity = view_model.health_severity

        self.health_status.setText(
            view_model.health_label
        )

        # CPU
        self.cpu_card.set_data(
            title="CPU",
            value=view_model.cpu_usage_display,
            status=(
                getattr(
                    view_model,
                    "cpu_status",
                    None,
                )
                or "Unknown"
            ),
            detail="Current CPU usage",
            status_severity=self.health_severity,
        )

        # Memory
        memory_capacity_display = getattr(
            view_model,
            "memory_capacity_display",
            "N/A",
        )

        self.memory_card.set_data(
            title="Memory",
            value=view_model.memory_usage_display,
            status=view_model.health_label,
            detail=memory_capacity_display,
            status_severity=self.health_severity,
        )

        # Storage
        self.storage_card.set_data(
            title="Storage",
            value=view_model.storage_usage_display,
            status=view_model.health_label,
            detail=view_model.storage_free_display,
            status_severity=self.health_severity,
        )

        # Storage Presentation References
        self.storage_capacity.setText(
            view_model.storage_capacity_display
        )

        self.storage_free.setText(
            view_model.storage_free_display
        )

        # Diagnostic Insight
        if view_model.primary_insight is None:
            self.diagnostic_insight_card.content.setText(
                "No significant diagnostic issue detected."
            )

            self.diagnostic_insight_card.set_status_severity(
                "info"
            )

        else:
            insight = view_model.primary_insight

            self.diagnostic_insight_card.content.setText(
                insight.get(
                    "issue",
                    insight.get(
                        "message",
                        "",
                    ),
                )
            )

            self.diagnostic_insight_card.set_status_severity(
                insight.get(
                    "severity",
                    view_model.health_severity,
                ).lower()
            )

        # Root Cause
        if view_model.primary_root_cause is None:
            self.root_cause_card.content.setText(
                "No primary root cause identified."
            )

            self.root_cause_card.set_status_severity(
                "info"
            )

        else:
            root_cause = (
                view_model.primary_root_cause
            )

            self.root_cause_card.content.setText(
                root_cause.get(
                    "root_cause",
                    root_cause.get(
                        "cause",
                        root_cause.get(
                            "description",
                            "",
                        ),
                    ),
                )
            )

            self.root_cause_card.set_status_severity(
                root_cause.get(
                    "severity",
                    view_model.health_severity,
                ).lower()
            )

        # Recommendation
        if view_model.primary_recommendation is None:
            self.recommendation_card.content.setText(
                "No recommendation available."
            )

            self.recommendation_card.set_status_severity(
                "info"
            )

        else:
            recommendation = (
                view_model.primary_recommendation
            )

            self.recommendation_card.content.setText(
                recommendation.get(
                    "recommendation",
                    recommendation.get(
                        "action",
                        recommendation.get(
                            "description",
                            "",
                        ),
                    ),
                )
            )

            self.recommendation_card.set_status_severity(
                recommendation.get(
                    "severity",
                    view_model.health_severity,
                ).lower()
            )