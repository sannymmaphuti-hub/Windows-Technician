from engine.dashboard_view_model import DashboardViewModel
from engine.technician_dashboard_presenter import (
    TechnicianDashboardPresenter,
)


class ApplicationStateStub:
    active_machine_id = "MACHINE-1"
    active_case_id = "CASE-1"


def create_view_model():
    return DashboardViewModel(
        ApplicationStateStub(),
        {
            "health": {
                "status": "HEALTHY",
                "score": 95,
            },
            "active_cases": [
                {"case_id": "CASE-001"},
            ],
            "fleet_alerts": [
                {"alert_id": "ALERT-001"},
            ],
            "unresolved_problems": [
                {"problem_id": "PROBLEM-001"},
            ],
            "remediation_status": [
                {"action_id": "ACTION-001"},
            ],
            "verification_status": [
                {"action_id": "ACTION-001"},
            ],
            "recent_activity": [
                {"activity_id": "ACT-001"},
            ],
        },
    )


def test_presenter_exposes_dashboard_surfaces():
    presenter = TechnicianDashboardPresenter(
        create_view_model()
    )

    assert presenter.active_cases() == [
        {"case_id": "CASE-001"}
    ]

    assert presenter.fleet_alerts() == [
        {"alert_id": "ALERT-001"}
    ]

    assert presenter.unresolved_problems() == [
        {"problem_id": "PROBLEM-001"}
    ]

    assert presenter.remediation_status() == [
        {"action_id": "ACTION-001"}
    ]

    assert presenter.verification_status() == [
        {"action_id": "ACTION-001"}
    ]

    assert presenter.recent_activity() == [
        {"activity_id": "ACT-001"}
    ]


def test_presenter_snapshot_is_complete():
    presenter = TechnicianDashboardPresenter(
        create_view_model()
    )

    assert set(presenter.snapshot()) == {
        "health",
        "active_cases",
        "fleet_alerts",
        "unresolved_problems",
        "remediation_status",
        "verification_status",
        "recent_activity",
    }


def test_presenter_is_defensive():
    presenter = TechnicianDashboardPresenter(
        create_view_model()
    )

    snapshot = presenter.snapshot()

    snapshot["active_cases"][0]["case_id"] = "CORRUPTED"

    assert presenter.active_cases() == [
        {"case_id": "CASE-001"}
    ]


def test_presenter_contains_no_operational_actions():
    presenter = TechnicianDashboardPresenter(
        create_view_model()
    )

    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert not forbidden.intersection(dir(presenter))
