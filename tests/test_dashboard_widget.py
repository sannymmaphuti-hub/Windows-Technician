from application.app import TechnicianApp
from gui.dashboard import DashboardWidget
from types import SimpleNamespace


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

def test_dashboard_receives_dashboard_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

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

def test_dashboard_can_update_dashboard_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

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

def test_dashboard_updates_health_severity_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.health_severity == view_model.health_severity

def test_dashboard_updates_execution_state_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.execution_state == view_model.execution_state

def test_dashboard_updates_execution_label_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.execution_label == view_model.execution_label

def test_dashboard_updates_execution_severity_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.execution_severity == view_model.execution_severity

def test_dashboard_has_execution_status(qtbot):
    app = TechnicianApp()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    assert dashboard.execution_status is not None

def test_dashboard_updates_execution_status_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.execution_status.text() == view_model.execution_label

def test_dashboard_updates_statuses_together_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

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

def test_dashboard_updates_primary_insight_from_view_model(qtbot):
    app = TechnicianApp()
    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    app.run_diagnostics()
    view_model = app.get_dashboard_view_model()

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

def test_dashboard_updates_primary_root_cause_from_view_model(qtbot):
    app = TechnicianApp()
    dashboard = DashboardWidget(app)
    qtbot.addWidget(dashboard)

    app.run_diagnostics()
    view_model = app.get_dashboard_view_model()

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

def test_dashboard_updates_metric_cards_from_view_model(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.cpu_card.value.text() == view_model.cpu_usage_display
    assert dashboard.memory_card.value.text() == view_model.memory_usage_display
    assert dashboard.storage_card.value.text() == view_model.storage_usage_display

def test_dashboard_metric_cards_receive_status_severity(
    qtbot
):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert (
        dashboard.memory_card.status_severity
        == view_model.health_severity
    )

    assert (
        dashboard.storage_card.status_severity
        == view_model.health_severity
    )

def test_dashboard_cpu_card_receives_cpu_status(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.cpu_card.status.text() == (
        view_model.cpu_status or "Unknown"
    )

def test_dashboard_memory_card_receives_health_status(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

    dashboard.set_view_model(view_model)

    assert dashboard.memory_card.status.text() == (
        view_model.health_label
    )


def test_dashboard_storage_card_receives_health_status(qtbot):
    app = TechnicianApp()

    app.run_diagnostics()

    view_model = app.get_dashboard_view_model()

    dashboard = DashboardWidget(app)

    qtbot.addWidget(dashboard)

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