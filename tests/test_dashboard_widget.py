from PySide6.QtWidgets import QLabel
import pytest

pytest.importorskip("PySide6")

from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_widget import DashboardWidget
from engine.diagnostic_card_widget import DiagnosticCardWidget


@pytest.fixture
def qapp():
    from PySide6.QtWidgets import QApplication, QLabel, QLabel

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def make_view_model():
    state = ApplicationState()

    intelligence = {
        "health": {
            "status": "WARNING",
            "score": 72,
        },
        "system_findings": [
            {
                "finding_id": "F-001",
                "severity": "HIGH",
                "category": "MEMORY",
                "title": "High memory pressure",
                "explanation": "Available memory is low.",
                "evidence": [{"memory_percent": 88}],
                "next_step": "Review memory-intensive applications.",
            },
            {
                "finding_id": "F-002",
                "severity": "MEDIUM",
                "category": "CPU",
                "title": "Elevated CPU activity",
                "explanation": "CPU utilization is elevated.",
                "evidence": [{"cpu_percent": 82}],
                "next_step": "Review active processes.",
            },
        ],
        "relationships": [
            {
                "source": "MEMORY",
                "target": "PERFORMANCE",
            }
        ],
        "root_causes": [
            {
                "cause_type": "RESOURCE_PRESSURE",
                "category": "MEMORY",
            }
        ],
        "recommendations": [
            {
                "action": "Review memory-intensive applications.",
            }
        ],
    }

    return DashboardViewModel(state, intelligence)


def test_requires_view_model(qapp):
    with pytest.raises(ValueError):
        DashboardWidget(None)


def test_dashboard_creates_diagnostic_cards(qapp):
    widget = DashboardWidget(make_view_model())

    cards = widget.findChildren(DiagnosticCardWidget)

    assert len(cards) == 2


def test_diagnostic_card_content_is_visible(qapp):
    widget = DashboardWidget(make_view_model())

    text = widget.findChildren(DiagnosticCardWidget)[0].window().findChildren(
        type(widget.title_label)
    )

    assert widget.diagnostic_cards.count() == 2

    card = widget.findChildren(DiagnosticCardWidget)[0]

    assert card.severity_label.text() == "Severity: HIGH"
    assert card.category_label.text() == "Category: MEMORY"
    assert card.title_label.text() == "High memory pressure"


def test_dashboard_preserves_health(qapp):
    widget = DashboardWidget(make_view_model())

    assert "WARNING" in widget.health_label.text()
    assert "72" in widget.health_label.text()


def test_dashboard_preserves_relationships(qapp):
    widget = DashboardWidget(make_view_model())

    assert "MEMORY" in widget.relationships_label.text()
    assert "PERFORMANCE" in widget.relationships_label.text()


def test_dashboard_preserves_root_causes(qapp):
    widget = DashboardWidget(make_view_model())

    assert "RESOURCE_PRESSURE" in widget.root_causes_label.text()


def test_dashboard_preserves_recommendations(qapp):
    widget = DashboardWidget(make_view_model())

    assert "Review memory-intensive applications." in (
        widget.recommendations_label.text()
    )


def test_empty_findings_show_empty_state(qapp):
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "NORMAL",
                "score": 100,
            },
            "system_findings": [],
        },
    )

    widget = DashboardWidget(view_model)

    assert widget.diagnostic_cards.count() == 0

    empty_labels = [
        label
        for label in widget.findChildren(QLabel)
        if label.objectName() == "dashboardNoFindings"
    ]

    assert len(empty_labels) == 1
    assert empty_labels[0].text() == "No diagnostic findings detected."


def test_refresh_updates_diagnostic_cards(qapp):
    view_model = make_view_model()
    widget = DashboardWidget(view_model)

    assert widget.diagnostic_cards.count() == 2

    view_model.update_intelligence(
        {
            "health": {
                "status": "NORMAL",
                "score": 100,
            },
            "system_findings": [
                {
                    "finding_id": "F-003",
                    "severity": "LOW",
                    "category": "DISK",
                    "title": "Low disk space",
                    "explanation": "Disk space is declining.",
                    "evidence": [{"free_gb": 12}],
                    "next_step": "Review large files.",
                }
            ],
        }
    )

    widget.refresh()

    cards = widget.findChildren(DiagnosticCardWidget)

    assert len(cards) == 1
    assert cards[0].title_label.text() == "Low disk space"


def test_to_dict_reports_card_count(qapp):
    widget = DashboardWidget(make_view_model())

    result = widget.to_dict()

    assert result["diagnostic_card_count"] == 2
    assert result["summary"]["finding_count"] == 2


def test_widget_remains_presentation_only():
    declared_names = set(DashboardWidget.__dict__)

    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "recommend",
        "authorize",
        "remediate",
        "execute",
    }

    for name in forbidden:
        assert not any(
            name in attribute.lower()
            for attribute in declared_names
        )


def test_dashboard_does_not_modify_view_model(qapp):
    view_model = make_view_model()
    before = view_model.to_dict()

    widget = DashboardWidget(view_model)
    widget.refresh()

    assert view_model.to_dict() == before






