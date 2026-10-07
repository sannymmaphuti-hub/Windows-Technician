import pytest

from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_remediation_actions import (
    DashboardRemediationActions,
)
from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)


def make_view_model(actions):
    return DashboardViewModel(
        ApplicationState(),
        {
            "health": {
                "status": "WARNING",
                "score": 74,
            },
            "system_findings": [],
            "remediation_actions": actions,
        },
    )


def test_requires_dashboard_view_model():
    with pytest.raises(ValueError):
        DashboardRemediationActions(None)


def test_empty_actions_are_supported():
    adapter = DashboardRemediationActions(
        make_view_model([])
    )

    assert adapter.count() == 0
    assert adapter.models() == []


def test_missing_actions_are_supported():
    view_model = DashboardViewModel(
        ApplicationState(),
        {"health": {"status": "NORMAL"}},
    )

    adapter = DashboardRemediationActions(view_model)

    assert adapter.count() == 0


def test_one_model_is_created_per_valid_action():
    actions = [
        {
            "action_id": "A1",
            "action_type": "memory_review",
        },
        {
            "action_id": "A2",
            "action_type": "service_review",
        },
    ]

    adapter = DashboardRemediationActions(
        make_view_model(actions)
    )

    assert adapter.count() == 2
    assert all(
        isinstance(model, RemediationPresentationModel)
        for model in adapter.models()
    )


def test_invalid_action_entries_are_ignored():
    actions = [
        {
            "action_id": "A1",
            "action_type": "memory_review",
        },
        None,
        "invalid",
        42,
    ]

    adapter = DashboardRemediationActions(
        make_view_model(actions)
    )

    assert adapter.count() == 1


def test_action_data_is_preserved():
    actions = [
        {
            "action_id": "A1",
            "action_type": "memory_review",
            "title": "Review memory",
            "risk": "HIGH",
        }
    ]

    adapter = DashboardRemediationActions(
        make_view_model(actions)
    )

    model = adapter.models()[0]

    assert model.action_id() == "A1"
    assert model.action_type() == "memory_review"
    assert model.title() == "Review memory"
    assert model.risk() == "HIGH"


def test_models_returns_defensive_list():
    adapter = DashboardRemediationActions(
        make_view_model(
            [{"action_id": "A1"}]
        )
    )

    models = adapter.models()
    models.clear()

    assert adapter.count() == 1


def test_refresh_reads_updated_intelligence():
    view_model = make_view_model(
        [{"action_id": "A1"}]
    )

    adapter = DashboardRemediationActions(view_model)

    assert adapter.count() == 1

    view_model.update_intelligence(
        {
            "remediation_actions": [
                {"action_id": "A2"},
                {"action_id": "A3"},
            ]
        }
    )

    adapter.refresh()

    assert adapter.count() == 2
    assert [
        model.action_id()
        for model in adapter.models()
    ] == ["A2", "A3"]


def test_to_dict_returns_presentation_data():
    adapter = DashboardRemediationActions(
        make_view_model(
            [
                {
                    "action_id": "A1",
                    "action_type": "memory_review",
                    "risk": "HIGH",
                }
            ]
        )
    )

    result = adapter.to_dict()

    assert len(result) == 1
    assert result[0]["action_id"] == "A1"
    assert result[0]["risk"] == "HIGH"


def test_adapter_has_no_execution_surface():
    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "retry",
        "verify",
        "run",
    }

    public_methods = {
        name
        for name in dir(DashboardRemediationActions)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)
