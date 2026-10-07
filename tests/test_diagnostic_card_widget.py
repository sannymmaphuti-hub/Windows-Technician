import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from engine.diagnostic_card_model import DiagnosticCardModel
from engine.diagnostic_card_widget import DiagnosticCardWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def make_card(finding=None):
    if finding is None:
        finding = {
            "finding_id": "F-001",
            "severity": "HIGH",
            "category": "MEMORY",
            "title": "High memory pressure",
            "explanation": "Available memory is low.",
            "evidence": [
                {
                    "memory_percent": 88,
                    "available_gb": 0.6,
                }
            ],
            "next_step": "Review memory-intensive applications.",
        }

    return DiagnosticCardWidget(
        DiagnosticCardModel(finding)
    )


def test_requires_card_model(qapp):
    with pytest.raises(ValueError):
        DiagnosticCardWidget(None)


def test_displays_severity(qapp):
    widget = make_card()

    assert widget.severity_label.text() == "Severity: HIGH"


def test_displays_category(qapp):
    widget = make_card()

    assert widget.category_label.text() == "Category: MEMORY"


def test_displays_title(qapp):
    widget = make_card()

    assert widget.title_label.text() == "High memory pressure"


def test_displays_explanation(qapp):
    widget = make_card()

    assert widget.explanation_label.text() == (
        "Available memory is low."
    )


def test_displays_evidence(qapp):
    widget = make_card()

    text = widget.evidence_label.text()

    assert "Evidence:" in text
    assert "memory_percent: 88" in text
    assert "available_gb: 0.6" in text


def test_displays_next_step(qapp):
    widget = make_card()

    assert widget.next_step_label.text() == (
        "Next step: Review memory-intensive applications."
    )


def test_empty_evidence_has_safe_message(qapp):
    widget = make_card(
        {
            "title": "Startup issue",
            "evidence": [],
        }
    )

    assert widget.evidence_label.text() == (
        "Evidence: No evidence available."
    )


def test_scalar_evidence_is_displayed(qapp):
    widget = make_card(
        {
            "title": "Disk issue",
            "evidence": "Storage is nearly full.",
        }
    )

    assert "Storage is nearly full." in (
        widget.evidence_label.text()
    )


def test_refresh_updates_display(qapp):
    model = DiagnosticCardModel(
        {
            "severity": "LOW",
            "category": "SYSTEM",
            "title": "Initial finding",
            "explanation": "Initial explanation.",
            "next_step": "Initial next step.",
        }
    )

    widget = DiagnosticCardWidget(model)

    assert widget.title_label.text() == "Initial finding"

    model._finding["title"] = "Updated finding"
    model._finding["severity"] = "HIGH"

    widget.refresh()

    assert widget.title_label.text() == "Updated finding"
    assert widget.severity_label.text() == "Severity: HIGH"


def test_widget_uses_supplied_model(qapp):
    model = DiagnosticCardModel(
        {
            "title": "Memory pressure",
        }
    )

    widget = DiagnosticCardWidget(model)

    assert widget.card_model is model


def test_widget_is_presentation_only(qapp):
    declared_names = set(DiagnosticCardWidget.__dict__)

    forbidden = (
        "diagnose",
        "analyze",
        "recommend",
        "remediate",
        "execute",
        "authorize",
    )

    for name in forbidden:
        assert not any(
            name in attribute.lower()
            for attribute in declared_names
        )


def test_widget_does_not_modify_model(qapp):
    finding = {
        "severity": "HIGH",
        "title": "Memory pressure",
        "evidence": [
            {"memory": 88},
        ],
    }

    model = DiagnosticCardModel(finding)
    before = model.to_dict()

    widget = DiagnosticCardWidget(model)
    widget.refresh()

    assert model.to_dict() == before


def test_widget_has_accessible_text(qapp):
    widget = make_card()

    assert widget.title_label.text()
    assert widget.explanation_label.text()
    assert widget.evidence_label.text()
    assert widget.next_step_label.text()


def test_widget_is_frame_based(qapp):
    widget = make_card()

    assert widget.objectName() == "diagnosticCard"
