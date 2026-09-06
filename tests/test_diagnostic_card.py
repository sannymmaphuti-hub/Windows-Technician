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

def test_diagnostic_card_has_reasonable_minimum_height(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="High memory usage detected.",
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.minimumHeight() >= 80


def test_diagnostic_card_content_supports_word_wrapping(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content=(
            "This is a long diagnostic explanation that "
            "should remain readable inside the dashboard card."
        ),
        severity="warning",
    )

    qtbot.addWidget(card)

    assert card.content.wordWrap() is True


def test_diagnostic_card_title_supports_word_wrapping(qtbot):
    card = DiagnosticCard(
        title="Diagnostic Insight",
        content="Test content.",
        severity="info",
    )

    qtbot.addWidget(card)

    assert card.title.wordWrap() is True
