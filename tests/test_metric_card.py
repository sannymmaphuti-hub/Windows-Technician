from PySide6.QtWidgets import QLabel

from gui.metric_card import MetricCard


def test_metric_card_can_be_created(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    assert card is not None


def test_metric_card_has_title(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    assert isinstance(card.title, QLabel)
    assert card.title.text() == "CPU"


def test_metric_card_has_value(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    assert isinstance(card.value, QLabel)
    assert card.value.text() == "25.0%"


def test_metric_card_has_status(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    assert isinstance(card.status, QLabel)
    assert card.status.text() == "Normal"


def test_metric_card_has_detail(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    assert isinstance(card.detail, QLabel)
    assert card.detail.text() == "Processor usage"

def test_metric_card_can_update_data(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    card.set_data(
        title="Memory",
        value="42.0%",
        status="Healthy",
        detail="6.72 GB / 16.00 GB"
    )

    assert card.title.text() == "Memory"
    assert card.value.text() == "42.0%"
    assert card.status.text() == "Healthy"
    assert card.detail.text() == "6.72 GB / 16.00 GB"

def test_metric_card_stores_status_severity(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    card.set_status_severity("healthy")

    assert card.status_severity == "healthy"

def test_metric_card_set_data_updates_status_severity(qtbot):
    card = MetricCard(
        title="CPU",
        value="25.0%",
        status="Normal",
        detail="Processor usage"
    )

    qtbot.addWidget(card)

    card.set_status_severity("healthy")

    card.set_data(
        title="Memory",
        value="85.0%",
        status="Needs Attention",
        detail="High memory usage",
        status_severity="warning"
    )

    assert card.title.text() == "Memory"
    assert card.value.text() == "85.0%"
    assert card.status.text() == "Needs Attention"
    assert card.detail.text() == "High memory usage"
    assert card.status_severity == "warning"

def test_metric_card_can_apply_status_severity(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    card.set_status_severity("warning")

    assert card.status_severity == "warning"

def test_metric_card_applies_visual_state_for_warning(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    card.set_status_severity("warning")

    assert "warning" in card.property("statusSeverity")

def test_metric_card_supports_all_status_severities(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    for severity in (
        "healthy",
        "warning",
        "critical",
        "info"
    ):
        card.set_status_severity(severity)

        assert card.status_severity == severity
        assert card.property("statusSeverity") == severity

def test_metric_card_has_card_surface_style(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    stylesheet = card.styleSheet()

    assert stylesheet
    assert "border-radius" in stylesheet
    assert "padding" in stylesheet

def test_metric_card_has_internal_spacing(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    layout = card.layout()

    assert layout is not None
    assert layout.spacing() > 0
    assert layout.contentsMargins().left() > 0
    assert layout.contentsMargins().right() > 0

def test_metric_card_has_typography_hierarchy(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    assert card.value.font().pointSize() > card.title.font().pointSize()
    assert card.title.font().pointSize() > card.detail.font().pointSize()

def test_metric_card_status_is_bold(qtbot):
    card = MetricCard(
        title="Memory",
        value="84.1%",
        status="Needs Attention",
        detail="13.4 GB / 16.0 GB"
    )

    qtbot.addWidget(card)

    assert card.status.font().bold()