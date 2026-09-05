from PySide6.QtWidgets import QApplication

from gui.diagnostic_card import DiagnosticCard


def test_diagnostic_card_can_be_created(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card is not None


def test_diagnostic_card_stores_title(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.title.text() == "Diagnostic Insight"


def test_diagnostic_card_stores_content(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.content.text() == "High memory pressure"


def test_diagnostic_card_stores_severity(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.severity == "warning"

def test_diagnostic_card_exposes_status_severity_property(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.property("statusSeverity") == "warning"


def test_diagnostic_card_can_update_severity(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory pressure",
        severity="warning",
    )

    qtbot.addWidget(card)

    card.set_status_severity("critical")

    assert card.severity == "critical"
    assert card.property("statusSeverity") == "critical"