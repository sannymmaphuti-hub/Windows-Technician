import pytest

pytest.importorskip("PySide6")

from engine.application_state import ApplicationState
from engine.dashboard_diagnostic_cards import DashboardDiagnosticCards
from engine.dashboard_view_model import DashboardViewModel


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
    }

    return DashboardViewModel(state, intelligence)


def test_requires_dashboard_view_model():
    with pytest.raises(ValueError):
        DashboardDiagnosticCards(None)


def test_builds_one_card_per_finding():
    cards = DashboardDiagnosticCards(make_view_model())

    assert cards.count() == 2
    assert len(cards.cards()) == 2


def test_cards_are_diagnostic_card_models():
    cards = DashboardDiagnosticCards(make_view_model())

    assert all(
        card.__class__.__name__ == "DiagnosticCardModel"
        for card in cards.cards()
    )


def test_first_card_preserves_finding():
    cards = DashboardDiagnosticCards(make_view_model())

    card = cards.cards()[0]

    assert card.identifier() == "F-001"
    assert card.severity() == "HIGH"
    assert card.category() == "MEMORY"
    assert card.title() == "High memory pressure"


def test_second_card_preserves_finding():
    cards = DashboardDiagnosticCards(make_view_model())

    card = cards.cards()[1]

    assert card.identifier() == "F-002"
    assert card.severity() == "MEDIUM"
    assert card.category() == "CPU"


def test_empty_findings_produce_zero_cards():
    state = ApplicationState()
    view_model = DashboardViewModel(
        state,
        {
            "health": {"status": "NORMAL", "score": 100},
            "system_findings": [],
        },
    )

    cards = DashboardDiagnosticCards(view_model)

    assert cards.count() == 0
    assert cards.cards() == []


def test_invalid_finding_entries_are_ignored():
    state = ApplicationState()
    view_model = DashboardViewModel(
        state,
        {
            "system_findings": [
                {"title": "Valid finding"},
                "not a finding",
                None,
                123,
            ],
        },
    )

    cards = DashboardDiagnosticCards(view_model)

    assert cards.count() == 1


def test_refresh_rebuilds_cards():
    view_model = make_view_model()
    cards = DashboardDiagnosticCards(view_model)

    assert cards.count() == 2

    view_model.update_intelligence(
        {
            "system_findings": [
                {
                    "finding_id": "F-003",
                    "severity": "LOW",
                    "title": "New finding",
                }
            ]
        }
    )

    cards.refresh()

    assert cards.count() == 1
    assert cards.cards()[0].identifier() == "F-003"


def test_cards_are_defensive_from_internal_list():
    cards = DashboardDiagnosticCards(make_view_model())

    returned = cards.cards()
    returned.clear()

    assert cards.count() == 2


def test_presentation_adapter_has_no_execution_surface():
    declared_names = set(DashboardDiagnosticCards.__dict__)

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


def test_adapter_does_not_mutate_dashboard_view_model():
    view_model = make_view_model()
    before = view_model.to_dict()

    DashboardDiagnosticCards(view_model)

    assert view_model.to_dict() == before
