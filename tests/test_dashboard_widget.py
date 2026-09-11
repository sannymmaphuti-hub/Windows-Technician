from types import SimpleNamespace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QLabel, QPushButton
from application.app import TechnicianApp
from application.diagnostic_view import DiagnosticView
from application.dashboard_view_model import DashboardViewModel
from engine.remediation_operation import RemediationOperation
from application.app import TechnicianApp
from gui.dashboard import DashboardWidget




def test_dashboard_widget_can_be_created(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard is not None


def test_dashboard_widget_receives_technician_app(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.technician_app is app


def test_dashboard_widget_has_layout(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.layout() is not None


def test_dashboard_widget_has_reasonable_minimum_size(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.minimumWidth() >= 900
    assert dashboard.minimumHeight() >= 550


def test_dashboard_widget_has_header(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.header is not None


def test_dashboard_widget_has_content_area(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.content_area is not None


def test_dashboard_has_title(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.title is not None
    assert dashboard.title.text() == "System Overview"


def test_dashboard_has_health_summary(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.health_summary is not None


def test_dashboard_has_health_status(qtbot, monkeypatch):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.health_status is not None


def test_dashboard_receives_dashboard_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.view_model is view_model


def test_dashboard_creation_does_not_run_diagnostics(qtbot, monkeypatch):
    app = TechnicianApp()

    def fail_if_called():
        raise AssertionError(
            "Dashboard creation should not run diagnostics."
        )

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        fail_if_called
    )

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard is not None


def test_dashboard_can_update_dashboard_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.view_model is view_model


def test_dashboard_updates_health_status_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()
    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert (
        dashboard.health_status.text()
        == view_model.health_label
    )


def test_dashboard_updates_health_severity_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.health_severity == view_model.health_severity


def test_dashboard_updates_execution_state_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.execution_state == view_model.execution_state


def test_dashboard_updates_execution_label_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.execution_label == view_model.execution_label


def test_dashboard_updates_execution_severity_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.execution_severity == view_model.execution_severity


def test_dashboard_has_execution_status(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.execution_status is not None


def test_dashboard_updates_execution_status_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.execution_status.text() == view_model.execution_label


def test_dashboard_updates_statuses_together_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.health_status.text() == view_model.health_label
    assert dashboard.execution_status.text() == view_model.execution_label


def test_dashboard_starts_without_view_model(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.view_model is None


def test_dashboard_starts_with_ready_execution_status(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.execution_status.text() == "Ready"


def test_dashboard_has_cpu_usage(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.cpu_usage is not None


def test_dashboard_updates_cpu_usage_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    assert (
        dashboard.cpu_usage.text()
        == dashboard_view_model.cpu_usage_display
    )


def test_dashboard_has_memory_usage(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.memory_usage is not None


def test_dashboard_updates_memory_usage_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.memory_usage.text() == view_model.memory_usage_display


def test_dashboard_has_storage_usage(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "storage_usage")


def test_dashboard_updates_storage_usage_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.storage_usage.text() == view_model.storage_usage_display


def test_dashboard_has_storage_capacity(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "storage_capacity")


def test_dashboard_updates_storage_capacity_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert (
        dashboard.storage_capacity.text()
        == view_model.storage_capacity_display
    )


def test_dashboard_has_storage_free(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "storage_free")


def test_dashboard_updates_storage_free_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert (
        dashboard.storage_free.text()
        == view_model.storage_free_display
    )


def test_dashboard_has_primary_insight(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "primary_insight")


def test_dashboard_updates_primary_insight_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    expected_insight = view_model.primary_insight

    if expected_insight is None:
        assert dashboard.primary_insight.text() == (
            "No significant diagnostic issue detected."
        )
    else:
        assert dashboard.primary_insight.text() == (
            expected_insight.get(
                "issue",
                expected_insight.get("message", "")
            )
        )


def test_dashboard_has_primary_root_cause(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "primary_root_cause")


def test_dashboard_updates_primary_root_cause_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    expected_root_cause = view_model.primary_root_cause

    if expected_root_cause is None:
        assert dashboard.primary_root_cause.text() == (
            "No primary root cause identified."
        )
    else:
        assert dashboard.primary_root_cause.text() == (
            expected_root_cause.get(
                "root_cause",
                expected_root_cause.get(
                    "cause",
                    expected_root_cause.get(
                        "description",
                        ""
                    )
                )
            )
        )


def test_dashboard_has_primary_recommendation(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "primary_recommendation")


def test_dashboard_updates_primary_recommendation_from_view_model(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = SimpleNamespace(
        health_label="Healthy",
        health_severity="healthy",
        execution_state="COMPLETED",
        execution_label="Diagnostics Complete",
        execution_severity="healthy",
        cpu_usage_display="25.0%",
        memory_usage_display="40.0%",
        storage_usage_display="50.0%",
        storage_capacity_display="250.00 GB / 500.00 GB",
        storage_free_display="250.00 GB free",
        primary_insight=None,
        primary_root_cause=None,
        primary_recommendation={
            "recommendation": "Close unnecessary background applications."
        }
    )

    dashboard.set_view_model(view_model)

    assert (
        dashboard.primary_recommendation.text()
        == "Close unnecessary background applications."
    )


def test_dashboard_has_metric_cards(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(dashboard, "cpu_card")
    assert hasattr(dashboard, "memory_card")
    assert hasattr(dashboard, "storage_card")


def test_dashboard_metric_cards_are_in_layout(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None

    metric_layout = None

    for index in range(layout.count()):
        item = layout.itemAt(index)

        if item.layout() is not None:
            candidate = item.layout()

            if (
                candidate.indexOf(dashboard.cpu_card) != -1
                and candidate.indexOf(dashboard.memory_card) != -1
                and candidate.indexOf(dashboard.storage_card) != -1
            ):
                metric_layout = candidate
                break

    assert metric_layout is not None


def test_dashboard_updates_metric_cards_from_view_model(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.cpu_card.value.text() == view_model.cpu_usage_display
    assert dashboard.memory_card.value.text() == view_model.memory_usage_display
    assert dashboard.storage_card.value.text() == view_model.storage_usage_display


def test_dashboard_metric_cards_receive_status_severity(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert (
        dashboard.memory_card.status_severity
        == view_model.health_severity
    )

    assert (
        dashboard.storage_card.status_severity
        == view_model.health_severity
    )


def test_dashboard_cpu_card_receives_cpu_status(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.cpu_card.status.text() == (
        view_model.cpu_status or "Unknown"
    )


def test_dashboard_memory_card_receives_health_status(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.memory_card.status.text() == (
        view_model.health_label
    )


def test_dashboard_storage_card_receives_health_status(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    view_model = dashboard_view_model

    dashboard.set_view_model(view_model)

    assert dashboard.storage_card.status.text() == (
        view_model.health_label
    )


def test_dashboard_metric_cards_are_arranged_horizontally(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None

    metric_layout = None

    for index in range(layout.count()):
        item = layout.itemAt(index)

        if item.layout() is not None:
            candidate = item.layout()

            if (
                candidate.indexOf(dashboard.cpu_card) != -1
                and candidate.indexOf(dashboard.memory_card) != -1
                and candidate.indexOf(dashboard.storage_card) != -1
            ):
                metric_layout = candidate
                break

    assert metric_layout is not None

    assert metric_layout.__class__.__name__ == "QHBoxLayout"


def test_dashboard_metric_cards_share_horizontal_space(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None

    metric_layout = None

    for index in range(layout.count()):
        item = layout.itemAt(index)

        if item.layout() is not None:
            candidate = item.layout()

            if (
                candidate.indexOf(dashboard.cpu_card) != -1
                and candidate.indexOf(dashboard.memory_card) != -1
                and candidate.indexOf(dashboard.storage_card) != -1
            ):
                metric_layout = candidate
                break

    assert metric_layout is not None

    assert metric_layout.stretch(0) == 1
    assert metric_layout.stretch(1) == 1
    assert metric_layout.stretch(2) == 1


def test_dashboard_metric_cards_have_equal_widths(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.resize(1200, 700)
    dashboard.show()

    qtbot.waitExposed(dashboard)

    cpu_width = dashboard.cpu_card.width()
    memory_width = dashboard.memory_card.width()
    storage_width = dashboard.storage_card.width()

    assert cpu_width > 0
    assert memory_width > 0
    assert storage_width > 0

    assert abs(cpu_width - memory_width) <= 2
    assert abs(memory_width - storage_width) <= 2


def test_dashboard_has_named_surface_sections(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.header.objectName() == "DashboardHeader"
    assert dashboard.health_summary.objectName() == "HealthSummary"
    assert dashboard.content_area.objectName() == "DiagnosticContent"


def test_dashboard_surface_sections_follow_visual_hierarchy(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None

    header_index = layout.indexOf(dashboard.header)
    health_index = layout.indexOf(dashboard.health_summary)
    content_index = layout.indexOf(dashboard.content_area)

    assert header_index != -1
    assert health_index != -1
    assert content_index != -1

    assert header_index < health_index < content_index


def test_dashboard_metric_cards_follow_health_summary(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None

    health_index = layout.indexOf(dashboard.health_summary)

    metric_layout_index = -1

    for index in range(layout.count()):
        item = layout.itemAt(index)

        if item.layout() is not None:
            candidate = item.layout()

            if (
                candidate.indexOf(dashboard.cpu_card) != -1
                and candidate.indexOf(dashboard.memory_card) != -1
                and candidate.indexOf(dashboard.storage_card) != -1
            ):
                metric_layout_index = index
                break

    assert metric_layout_index != -1
    assert health_index < metric_layout_index


def test_dashboard_header_contains_only_identity_and_execution_status(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    header_layout = dashboard.header.layout()

    assert header_layout is not None

    assert header_layout.indexOf(dashboard.title) != -1
    assert header_layout.indexOf(dashboard.execution_status) != -1

    assert header_layout.indexOf(dashboard.cpu_usage) == -1


def test_dashboard_header_has_typographic_hierarchy(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert (
        dashboard.title.font().pointSize()
        > dashboard.execution_status.font().pointSize()
    )


def test_dashboard_header_title_is_bold(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.title.font().bold()


def test_dashboard_health_status_has_typographic_priority(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    health_font = dashboard.health_status.font()
    memory_font = dashboard.memory_usage.font()

    assert health_font.pointSize() > memory_font.pointSize()


def test_dashboard_health_status_is_bold(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.health_status.font().bold()


def test_dashboard_surface_sections_have_visual_surface_styling(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert "border-radius" in dashboard.header.styleSheet()
    assert "padding" in dashboard.header.styleSheet()

    assert "border-radius" in dashboard.health_summary.styleSheet()
    assert "padding" in dashboard.health_summary.styleSheet()

    assert "border-radius" in dashboard.content_area.styleSheet()
    assert "padding" in dashboard.content_area.styleSheet()


def test_dashboard_major_sections_have_spacing(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    assert layout is not None
    assert layout.spacing() > 0


def test_dashboard_diagnostic_insight_has_typographic_priority(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    insight_font = dashboard.primary_insight.font()
    root_cause_font = dashboard.primary_root_cause.font()
    recommendation_font = dashboard.primary_recommendation.font()

    assert insight_font.pointSize() > root_cause_font.pointSize()
    assert insight_font.pointSize() > recommendation_font.pointSize()


def test_dashboard_primary_insight_is_bold(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.primary_insight.font().bold()


def test_dashboard_has_diagnostic_insight_card(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.diagnostic_insight_card is not None


def test_dashboard_has_root_cause_card(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.root_cause_card is not None


def test_dashboard_has_recommendation_card(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.recommendation_card is not None

# ------------------------------------------------------------------
# Run Diagnostics Interaction Contract
# ------------------------------------------------------------------


def test_dashboard_has_run_diagnostics_button(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.run_diagnostics_button is not None


def test_dashboard_run_diagnostics_button_has_correct_label(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.run_diagnostics_button.text() == "Run Diagnostics"


def test_dashboard_run_diagnostics_button_starts_analysis(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    calls = []

    def fake_run_diagnostics():
        calls.append(True)

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        fake_run_diagnostics,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: calls == [True],
        timeout=1000,
    )


def test_dashboard_shows_analyzing_while_diagnostics_run(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    execution_states = []

    def fake_run_diagnostics():
        execution_states.append(
            dashboard.execution_status.text()
        )

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        fake_run_diagnostics,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: execution_states == ["Analyzing..."],
        timeout=1000,
    )


def test_dashboard_disables_run_button_during_diagnostics(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    button_states = []

    def fake_run_diagnostics():
        button_states.append(
            dashboard.run_diagnostics_button.isEnabled()
        )

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        fake_run_diagnostics,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: len(button_states) == 1,
        timeout=1000,
    )

    assert button_states == [False]


def test_dashboard_refreshes_after_successful_diagnostics(
    qtbot,
    monkeypatch,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        lambda: None,
    )

    monkeypatch.setattr(
        app,
        "get_dashboard_view_model",
        lambda: dashboard_view_model,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: dashboard.view_model is dashboard_view_model,
        timeout=1000,
    )

    assert dashboard.view_model is dashboard_view_model


def test_dashboard_shows_completed_after_successful_diagnostics(
    qtbot,
    monkeypatch,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        lambda: None,
    )

    monkeypatch.setattr(
        app,
        "get_dashboard_view_model",
        lambda: dashboard_view_model,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: dashboard.execution_state == "COMPLETED",
        timeout=1000,
    )

    assert dashboard.execution_label == "Diagnostics Complete"
    assert (
        dashboard.execution_status.text()
        == "Diagnostics Complete"
    )


def test_dashboard_reenables_run_button_after_success(
    qtbot,
    monkeypatch,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        lambda: None,
    )

    monkeypatch.setattr(
        app,
        "get_dashboard_view_model",
        lambda: dashboard_view_model,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: dashboard.run_diagnostics_button.isEnabled(),
        timeout=1000,
    )

    assert dashboard.run_diagnostics_button.isEnabled()


def test_dashboard_updates_health_after_successful_diagnostics(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    refreshed_view_model = DashboardViewModel(
        DiagnosticView(
            {
                "evidence": {},
                "diagnosis": {
                    "status": "WARNING",
                    "total_findings": 1,
                    "findings": [
                        {
                            "issue": "High memory usage detected.",
                            "severity": "WARNING",
                            "priority_score": 90,
                        }
                    ],
                    "correlations": [],
                    "root_causes": [],
                    "recommendations": [],
                },
                "diagnostic_case": {
                    "root_cause_candidates": [],
                    "primary_root_cause": None,
                },
                "case_decision": {},
            }
        ),
        execution_state="COMPLETED",
    )

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        lambda: None,
    )

    monkeypatch.setattr(
        app,
        "get_dashboard_view_model",
        lambda: refreshed_view_model,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: dashboard.view_model is refreshed_view_model,
        timeout=1000,
    )

    assert dashboard.health_status.text() == "Needs Attention"

    assert (
        dashboard.diagnostic_insight_card.content.text()
        == "High memory usage detected."
    )


def test_dashboard_remains_responsive_during_diagnostics(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    execution_started = []
    release_diagnostics = []

    def fake_run_diagnostics():
        execution_started.append(True)

        while not release_diagnostics:
            qtbot.wait(10)

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        fake_run_diagnostics,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: execution_started == [True],
        timeout=1000,
    )

    assert (
        dashboard.run_diagnostics_button.isEnabled()
        is False
    )

    release_diagnostics.append(True)

    qtbot.waitUntil(
        lambda: dashboard.run_diagnostics_button.isEnabled(),
        timeout=1000,
    )

    
def test_dashboard_diagnostic_worker_is_created(
    qtbot,
    monkeypatch,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    created = []

    from gui import dashboard as dashboard_module

    original_worker = dashboard_module.DiagnosticWorker

    def track_worker(technician_app):
        created.append(technician_app)
        return original_worker(technician_app)

    monkeypatch.setattr(
        dashboard_module,
        "DiagnosticWorker",
        track_worker,
    )

    monkeypatch.setattr(
        app,
        "run_diagnostics",
        lambda: None,
    )

    dashboard.run_diagnostics_button.click()

    qtbot.waitUntil(
        lambda: len(created) == 1,
        timeout=1000,
    )

    assert created == [app]

    qtbot.waitUntil(
        lambda: (
            dashboard._diagnostic_thread is None
            or not dashboard._diagnostic_thread.isRunning()
        ),
        timeout=2000,
    )

def test_dashboard_displays_remediation_action(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    assert hasattr(dashboard, "remediation_actions")
    assert len(dashboard.remediation_actions) == 1

def test_dashboard_remediation_action_preserves_lifecycle_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    displayed_action = dashboard.remediation_actions[0]

    assert displayed_action.authorization_status == "UNAUTHORIZED"
    assert displayed_action.execution_status == "NOT_EXECUTED"

def test_dashboard_has_remediation_actions_container(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert hasattr(
        dashboard,
        "remediation_actions_container",
    )
    assert dashboard.remediation_actions_container is not None

def test_dashboard_layout_contains_remediation_actions_container(
    qtbot,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    layout = dashboard.layout()

    widgets = [
        layout.itemAt(index).widget()
        for index in range(layout.count())
        if layout.itemAt(index).widget() is not None
    ]

    assert (
        dashboard.remediation_actions_container
        in widgets
    )

def test_dashboard_displays_remediation_action_description(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    labels = (
        dashboard.remediation_actions_container.findChildren(
            QLabel
        )
    )

    assert any(
        label.text()
        == "Review memory-intensive processes."
        for label in labels
    )

def test_dashboard_refreshing_remediation_actions_does_not_duplicate(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)
    dashboard.set_view_model(dashboard_view_model)

    labels = (
        dashboard.remediation_actions_container.findChildren(
            QLabel
        )
    )

    matching_labels = [
        label
        for label in labels
        if label.text()
        == "Review memory-intensive processes."
    ]

    assert len(matching_labels) == 1

def test_dashboard_displays_remediation_action_authorization_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    labels = (
        dashboard.remediation_actions_container.findChildren(
            QLabel
        )
    )

    assert any(
        "UNAUTHORIZED" in label.text()
        for label in labels
    )

def test_dashboard_displays_remediation_action_execution_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    labels = (
        dashboard.remediation_actions_container.findChildren(
            QLabel
        )
    )

    assert any(
        "NOT_EXECUTED" in label.text()
        for label in labels
    )

def test_dashboard_remediation_authorize_control_does_not_auto_authorize(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    assert action.authorization_status == "UNAUTHORIZED"

def test_dashboard_displays_remediation_authorize_control(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    assert any(
        "Authorize" in button.text()
        for button in buttons
    )

def test_dashboard_remediation_authorize_control_authorizes_action(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    authorize_button = next(
        button
        for button in buttons
        if "Authorize" in button.text()
    )

    qtbot.mouseClick(
        authorize_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.authorization_status == "AUTHORIZED"

def test_dashboard_remediation_authorize_control_updates_displayed_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    authorize_button = next(
        button
        for button in buttons
        if "Authorize" in button.text()
    )

    qtbot.mouseClick(
        authorize_button,
        Qt.MouseButton.LeftButton,
    )

    labels = (
        dashboard.remediation_actions_container.findChildren(
            QLabel
        )
    )

    assert any(
        "Authorization: AUTHORIZED" in label.text()
        for label in labels
    )

def test_dashboard_authorize_does_not_execute_remediation_action(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    authorize_button = next(
        button
        for button in buttons
        if "Authorize" in button.text()
    )

    qtbot.mouseClick(
        authorize_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_dashboard_displays_remediation_execute_control_when_authorized(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    assert any(
        "Execute" in button.text()
        for button in buttons
    )

def test_dashboard_remediation_execute_control_executes_authorized_action(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    buttons = (
        dashboard.remediation_actions_container.findChildren(
            QPushButton
        )
    )

    execute_button = next(
        button
        for button in buttons
        if "Execute" in button.text()
    )

    qtbot.mouseClick(
        execute_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.execution_status == "EXECUTED"

def test_dashboard_disables_execute_control_after_successful_execution(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    execute_button = next(
        button
        for button in (
            dashboard.remediation_actions_container.findChildren(
                QPushButton
            )
        )
        if "Execute" in button.text()
    )

    qtbot.mouseClick(
        execute_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.execution_status == "EXECUTED"
    assert execute_button.isEnabled() is False

def test_dashboard_displays_remediation_failure_reason(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.authorize()

    def failing_operation():
        raise RuntimeError(
            "Memory remediation failed."
        )

    app.technician.remediation_operation_registry._operations[
        "memory_review"
    ] = RemediationOperation(
        operation_id="memory_review",
        description="Failing memory remediation.",
        handler=failing_operation,
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    execute_button = next(
        button
        for button in (
            dashboard.remediation_actions_container.findChildren(
                QPushButton
            )
        )
        if "Execute" in button.text()
    )

    qtbot.mouseClick(
        execute_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.execution_status == "FAILED"

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "Memory remediation failed." in label.text()
        for label in labels
    )

def test_dashboard_denied_remediation_cannot_be_executed(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    action.deny()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    execute_button = next(
        button
        for button in (
            dashboard.remediation_actions_container.findChildren(
                QPushButton
            )
        )
        if "Execute" in button.text()
    )

    assert action.authorization_status == "DENIED"
    assert execute_button.isEnabled() is False

    qtbot.mouseClick(
        execute_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.execution_status == "NOT_EXECUTED"

def test_dashboard_unauthorized_remediation_cannot_be_executed(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": (
                "Review memory-intensive processes."
            ),
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    execute_button = next(
        button
        for button in (
            dashboard.remediation_actions_container.findChildren(
                QPushButton
            )
        )
        if "Execute" in button.text()
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert execute_button.isEnabled() is False

    qtbot.mouseClick(
        execute_button,
        Qt.MouseButton.LeftButton,
    )

    assert action.execution_status == "NOT_EXECUTED"

def test_dashboard_displays_remediation_binding_failure(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        }
    )

    action.category = "NETWORK"
    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    execute_button = None

    for index in range(
        dashboard.remediation_actions_layout.count()
    ):
        widget = (
            dashboard.remediation_actions_layout
            .itemAt(index)
            .widget()
        )

        if (
            isinstance(widget, QPushButton)
            and widget.text() == "Execute"
        ):
            execute_button = widget
            break

    assert execute_button is not None

    qtbot.mouseClick(
        execute_button,
        Qt.LeftButton,
    )

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "operation binding failed" in label.text().lower()
        for label in labels
    )

    assert action.execution_status == "NOT_EXECUTED"

def test_dashboard_displays_remediation_verification_result(
    qtbot,
    dashboard_view_model,
    monkeypatch,
):
    app = TechnicianApp()

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    verification_result = {
        "verified": True,
        "action_id": action.action_id,
        "expected": {"status": "NORMAL"},
        "observed": {"status": "NORMAL"},
        "reason": "Observed state matches expected state.",
    }

    class FakeRemediationResult:
        def __init__(self):
            self.execution_status = "EXECUTED"
            self.verification_result = verification_result

    def fake_remediate(current_action):
        current_action.execution_status = "EXECUTED"
        return FakeRemediationResult()

    monkeypatch.setattr(
        app.technician,
        "remediate",
        fake_remediate,
    )

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    execute_button = None

    for index in range(
        dashboard.remediation_actions_layout.count()
    ):
        widget = (
            dashboard.remediation_actions_layout
            .itemAt(index)
            .widget()
        )

        if (
            isinstance(widget, QPushButton)
            and widget.text() == "Execute"
        ):
            execute_button = widget
            break

    assert execute_button is not None

    qtbot.mouseClick(
        execute_button,
        Qt.LeftButton,
    )

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "verification" in label.text().lower()
        for label in labels
    )

    assert any(
        "passed" in label.text().lower()
        for label in labels
    )

def test_dashboard_displays_remediation_verification_failure(
    qtbot,
    dashboard_view_model,
    monkeypatch,
):
    app = TechnicianApp()

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    verification_result = {
        "verified": False,
        "action_id": action.action_id,
        "expected": {"status": "NORMAL"},
        "observed": {"status": "WARNING"},
        "reason": "Observed state does not match expected state.",
    }

    class FakeRemediationResult:
        def __init__(self):
            self.execution_status = "EXECUTED"
            self.verification_result = verification_result

    def fake_remediate(current_action):
        current_action.execution_status = "EXECUTED"
        return FakeRemediationResult()

    monkeypatch.setattr(
        app.technician,
        "remediate",
        fake_remediate,
    )

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    execute_button = None

    for index in range(
        dashboard.remediation_actions_layout.count()
    ):
        widget = (
            dashboard.remediation_actions_layout
            .itemAt(index)
            .widget()
        )

        if (
            isinstance(widget, QPushButton)
            and widget.text() == "Execute"
        ):
            execute_button = widget
            break

    assert execute_button is not None

    qtbot.mouseClick(
        execute_button,
        Qt.LeftButton,
    )

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "verification" in label.text().lower()
        for label in labels
    )

    assert any(
        "failed" in label.text().lower()
        for label in labels
    )

def test_dashboard_refresh_preserves_remediation_lifecycle_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        }
    )

    dashboard_view_model.remediation_actions = [action]

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "authorization: authorized" in label.text().lower()
        for label in labels
    )

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_dashboard_refresh_preserves_executed_remediation_state(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    action = app.technician.remediation_action_planner.create_action(
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        }
    )

    action.authorize()

    dashboard_view_model.remediation_actions = [action]

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    app.technician.bind_remediation_operation(action)

    result = app.technician.remediate(action)

    assert result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"

    dashboard_view_model.remediation_actions = [action]

    dashboard.set_view_model(dashboard_view_model)

    labels = dashboard.remediation_actions_container.findChildren(
        QLabel
    )

    assert any(
        "execution: executed" in label.text().lower()
        for label in labels
    )

    assert action.execution_status == "EXECUTED"

def test_dashboard_multiple_remediation_actions_keep_controls_bound_to_correct_actions(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    first_action = (
        app.technician.remediation_action_planner.create_action(
            {
                "category": "MEMORY",
                "severity": "WARNING",
                "recommendation": "Review memory-intensive processes.",
            }
        )
    )

    second_action = (
        app.technician.remediation_action_planner.create_action(
            {
                "category": "MEMORY",
                "severity": "CRITICAL",
                "recommendation": "Investigate critical memory pressure.",
            }
        )
    )

    dashboard_view_model.remediation_actions = [
        first_action,
        second_action,
    ]

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    authorize_buttons = [
        widget
        for index in range(
            dashboard.remediation_actions_layout.count()
        )
        if (
            widget := (
                dashboard.remediation_actions_layout
                .itemAt(index)
                .widget()
            )
        )
        and isinstance(widget, QPushButton)
        and widget.text() == "Authorize"
    ]

    assert len(authorize_buttons) == 2

    qtbot.mouseClick(
        authorize_buttons[0],
        Qt.LeftButton,
    )

    assert first_action.authorization_status == "AUTHORIZED"
    assert second_action.authorization_status == "UNAUTHORIZED"

def test_dashboard_multiple_remediation_actions_authorize_correct_execute_control(
    qtbot,
    dashboard_view_model,
):
    app = TechnicianApp()

    first_action = (
        app.technician.remediation_action_planner.create_action(
            {
                "category": "MEMORY",
                "severity": "WARNING",
                "recommendation": "Review memory-intensive processes.",
            }
        )
    )

    second_action = (
        app.technician.remediation_action_planner.create_action(
            {
                "category": "MEMORY",
                "severity": "CRITICAL",
                "recommendation": "Investigate critical memory pressure.",
            }
        )
    )

    dashboard_view_model.remediation_actions = [
        first_action,
        second_action,
    ]

    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    dashboard.set_view_model(dashboard_view_model)

    authorize_buttons = []
    execute_buttons = []

    for index in range(
        dashboard.remediation_actions_layout.count()
    ):
        widget = (
            dashboard.remediation_actions_layout
            .itemAt(index)
            .widget()
        )

        if isinstance(widget, QPushButton):
            if widget.text() == "Authorize":
                authorize_buttons.append(widget)

            elif widget.text() == "Execute":
                execute_buttons.append(widget)

    assert len(authorize_buttons) == 2
    assert len(execute_buttons) == 2

    assert not execute_buttons[0].isEnabled()
    assert not execute_buttons[1].isEnabled()

    qtbot.mouseClick(
        authorize_buttons[0],
        Qt.LeftButton,
    )

    assert first_action.authorization_status == "AUTHORIZED"
    assert second_action.authorization_status == "UNAUTHORIZED"

    assert execute_buttons[0].isEnabled()
    assert not execute_buttons[1].isEnabled()

def test_dashboard_displays_remediation_audit(
    qtbot,
):
    dashboard = DashboardWidget(
        TechnicianApp()
    )

    qtbot.addWidget(dashboard)

    result = {
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 0,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
        },
        "case_decision": {},
        "remediation_actions": [],
        "remediation_audit": [
            {
                "action_id": "action_001",
                "execution_status": "EXECUTED",
                "reason": None,
                "verification_result": None,
            }
        ],
    }

    diagnostic_view = DiagnosticView(result)

    view_model = DashboardViewModel(
        diagnostic_view,
        execution_state="COMPLETED",
    )

    dashboard.set_view_model(view_model)

    audit_labels = (
        dashboard.remediation_audit_container
        .findChildren(QLabel)
    )

    assert any(
        "action_001" in label.text()
        for label in audit_labels
    )