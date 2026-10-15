import pytest

from engine.application_bootstrap import (
    ApplicationBootstrap,
)
from engine.dashboard_view_model import (
    DashboardViewModel,
)


def create_state():
    bootstrap = ApplicationBootstrap()
    bootstrap.start()
    return bootstrap.state


def test_dashboard_requires_application_state():
    with pytest.raises(ValueError):
        DashboardViewModel(None)


def test_dashboard_starts_empty():
    dashboard = DashboardViewModel(
        create_state()
    )

    assert dashboard.intelligence == {}
    assert dashboard.health() == {}
    assert dashboard.findings() == []
    assert dashboard.relationships() == []
    assert dashboard.root_causes() == []
    assert dashboard.recommendations() == []


def test_dashboard_accepts_intelligence():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "HEALTHY",
                "score": 100,
            },
            "system_findings": [
                {
                    "domain": "MEMORY",
                    "severity": "WARNING",
                }
            ],
            "relationships": [
                {
                    "type": "RESOURCE_INTERACTION",
                }
            ],
            "root_causes": [
                {
                    "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
                }
            ],
            "recommendations": [
                {
                    "priority": "HIGH",
                }
            ],
        },
    )

    assert dashboard.health() == {
        "status": "HEALTHY",
        "score": 100,
    }

    assert len(
        dashboard.findings()
    ) == 1

    assert len(
        dashboard.relationships()
    ) == 1

    assert len(
        dashboard.root_causes()
    ) == 1

    assert len(
        dashboard.recommendations()
    ) == 1


def test_update_intelligence():
    dashboard = DashboardViewModel(
        create_state()
    )

    dashboard.update_intelligence(
        {
            "health": {
                "status": "DEGRADED",
                "score": 70,
            }
        }
    )

    assert dashboard.health() == {
        "status": "DEGRADED",
        "score": 70,
    }


def test_update_none_clears_intelligence():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "HEALTHY",
            }
        },
    )

    dashboard.update_intelligence(None)

    assert dashboard.intelligence == {}


def test_invalid_intelligence_is_rejected():
    dashboard = DashboardViewModel(
        create_state()
    )

    with pytest.raises(ValueError):
        dashboard.update_intelligence([])


def test_health_missing_returns_empty_dict():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "system_findings": [],
        },
    )

    assert dashboard.health() == {}


def test_invalid_health_payload_is_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": "invalid",
        },
    )

    assert dashboard.health() == {}


def test_invalid_findings_payload_is_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "system_findings": {},
        },
    )

    assert dashboard.findings() == []


def test_invalid_relationships_payload_is_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "relationships": {},
        },
    )

    assert dashboard.relationships() == []


def test_invalid_root_causes_payload_is_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "root_causes": {},
        },
    )

    assert dashboard.root_causes() == []


def test_invalid_recommendations_payload_is_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "recommendations": {},
        },
    )

    assert dashboard.recommendations() == []


def test_dashboard_returns_defensive_health_copy():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "HEALTHY",
                "score": 100,
            }
        },
    )

    health = dashboard.health()
    health["score"] = 0

    assert dashboard.health()["score"] == 100


def test_dashboard_returns_defensive_findings_copy():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "system_findings": [
                {
                    "severity": "HIGH",
                }
            ]
        },
    )

    findings = dashboard.findings()
    findings[0]["severity"] = "LOW"

    assert (
        dashboard.findings()[0]["severity"]
        == "HIGH"
    )


def test_dashboard_returns_defensive_relationship_copy():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "relationships": [
                {
                    "type": "RESOURCE_INTERACTION",
                }
            ]
        },
    )

    relationships = dashboard.relationships()
    relationships[0]["type"] = "OTHER"

    assert (
        dashboard.relationships()[0]["type"]
        == "RESOURCE_INTERACTION"
    )


def test_dashboard_returns_defensive_root_cause_copy():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "root_causes": [
                {
                    "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
                }
            ]
        },
    )

    root_causes = dashboard.root_causes()
    root_causes[0]["cause_type"] = "OTHER"

    assert (
        dashboard.root_causes()[0]["cause_type"]
        == "PROCESS_RESOURCE_CONSUMPTION"
    )


def test_dashboard_returns_defensive_recommendation_copy():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "recommendations": [
                {
                    "priority": "HIGH",
                }
            ]
        },
    )

    recommendations = dashboard.recommendations()
    recommendations[0]["priority"] = "LOW"

    assert (
        dashboard.recommendations()[0]["priority"]
        == "HIGH"
    )


def test_summary_with_no_intelligence():
    dashboard = DashboardViewModel(
        create_state()
    )

    assert dashboard.summary() == {
        "status": "UNKNOWN",
        "health_score": None,
        "finding_count": 0,
        "relationship_count": 0,
        "root_cause_count": 0,
        "recommendation_count": 0,
        "machine_id": None,
        "case_id": None,
    }


def test_summary_reflects_intelligence():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "DEGRADED",
                "score": 65,
            },
            "system_findings": [
                {},
                {},
            ],
            "relationships": [
                {},
            ],
            "root_causes": [
                {},
            ],
            "recommendations": [
                {},
                {},
                {},
            ],
        },
    )

    summary = dashboard.summary()

    assert summary == {
        "status": "DEGRADED",
        "health_score": 65,
        "finding_count": 2,
        "relationship_count": 1,
        "root_cause_count": 1,
        "recommendation_count": 3,
        "machine_id": None,
        "case_id": None,
    }


def test_summary_includes_active_context():
    state = create_state()

    state.set_active_machine(
        "machine-01"
    )
    state.set_active_case(
        "case-01"
    )

    dashboard = DashboardViewModel(
        state
    )

    summary = dashboard.summary()

    assert summary["machine_id"] == (
        "MACHINE-01"
    )
    assert summary["case_id"] == (
        "CASE-01"
    )


def test_dashboard_to_dict():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "HEALTHY",
                "score": 100,
            }
        },
    )

    data = dashboard.to_dict()

    assert data["health"]["status"] == (
        "HEALTHY"
    )
    assert data["summary"]["health_score"] == 100


def test_dashboard_has_no_diagnostic_execution_surface():
    dashboard = DashboardViewModel(
        create_state()
    )

    assert not hasattr(
        dashboard,
        "diagnose",
    )
    assert not hasattr(
        dashboard,
        "analyze",
    )
    assert not hasattr(
        dashboard,
        "execute",
    )
    assert not hasattr(
        dashboard,
        "remediate",
    )


def test_dashboard_does_not_generate_recommendations():
    dashboard = DashboardViewModel(
        create_state()
    )

    assert not hasattr(
        dashboard,
        "generate_recommendations",
    )


def test_dashboard_does_not_change_application_state():
    state = create_state()

    dashboard = DashboardViewModel(
        state,
        {
            "health": {
                "status": "DEGRADED",
            }
        },
    )

    before = state.to_dict()

    dashboard.summary()

    assert state.to_dict() == before


def test_dashboard_can_present_system_wide_intelligence():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "health": {
                "status": "DEGRADED",
                "score": 55,
            },
            "system_findings": [
                {
                    "domain": "MEMORY",
                    "severity": "WARNING",
                },
                {
                    "domain": "PROCESS",
                    "severity": "HIGH",
                },
            ],
            "relationships": [
                {
                    "type": "RESOURCE_INTERACTION",
                    "confidence": "MEDIUM",
                }
            ],
            "root_causes": [
                {
                    "cause_type": "PROCESS_RESOURCE_CONSUMPTION",
                    "confidence": "MEDIUM",
                }
            ],
            "recommendations": [
                {
                    "priority": "HIGH",
                    "action": "Investigate resource pressure.",
                }
            ],
        },
    )

    summary = dashboard.summary()

    assert summary["status"] == "DEGRADED"
    assert summary["health_score"] == 55
    assert summary["finding_count"] == 2
    assert summary["relationship_count"] == 1
    assert summary["root_cause_count"] == 1
    assert summary["recommendation_count"] == 1

# ==========================================================
# V1.0 Technician Dashboard Contract
# ==========================================================

def test_v1_dashboard_surfaces_default_to_empty():
    dashboard = DashboardViewModel(
        create_state()
    )

    assert dashboard.active_cases() == []
    assert dashboard.fleet_alerts() == []
    assert dashboard.unresolved_problems() == []
    assert dashboard.remediation_status() == []
    assert dashboard.verification_status() == []
    assert dashboard.recent_activity() == []


def test_v1_dashboard_surfaces_accept_production_projections():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "active_cases": [
                {"case_id": "CASE-001"}
            ],
            "fleet_alerts": [
                {"alert_id": "ALERT-001"}
            ],
            "unresolved_problems": [
                {"problem_id": "PROBLEM-001"}
            ],
            "remediation_status": [
                {
                    "action_id": "ACTION-001",
                    "authorization_status": "AUTHORIZED",
                    "execution_status": "EXECUTED",
                }
            ],
            "verification_status": [
                {
                    "action_id": "ACTION-001",
                    "status": "VERIFIED",
                }
            ],
            "recent_activity": [
                {
                    "activity_id": "ACT-001",
                    "type": "CASE_UPDATED",
                }
            ],
        },
    )

    assert dashboard.active_cases() == [
        {"case_id": "CASE-001"}
    ]

    assert dashboard.fleet_alerts() == [
        {"alert_id": "ALERT-001"}
    ]

    assert dashboard.unresolved_problems() == [
        {"problem_id": "PROBLEM-001"}
    ]

    assert dashboard.remediation_status() == [
        {
            "action_id": "ACTION-001",
            "authorization_status": "AUTHORIZED",
            "execution_status": "EXECUTED",
        }
    ]

    assert dashboard.verification_status() == [
        {
            "action_id": "ACTION-001",
            "status": "VERIFIED",
        }
    ]

    assert dashboard.recent_activity() == [
        {
            "activity_id": "ACT-001",
            "type": "CASE_UPDATED",
        }
    ]


def test_v1_dashboard_surfaces_are_defensive():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "active_cases": [
                {"case_id": "CASE-001"}
            ],
            "fleet_alerts": [
                {"alert_id": "ALERT-001"}
            ],
            "recent_activity": [
                {"type": "CASE_UPDATED"}
            ],
        },
    )

    cases = dashboard.active_cases()
    alerts = dashboard.fleet_alerts()
    activity = dashboard.recent_activity()

    cases[0]["case_id"] = "MUTATED"
    alerts[0]["alert_id"] = "MUTATED"
    activity[0]["type"] = "MUTATED"

    assert dashboard.active_cases()[0]["case_id"] == "CASE-001"
    assert dashboard.fleet_alerts()[0]["alert_id"] == "ALERT-001"
    assert dashboard.recent_activity()[0]["type"] == "CASE_UPDATED"


def test_v1_dashboard_invalid_surface_payloads_are_ignored():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "active_cases": {},
            "fleet_alerts": "invalid",
            "unresolved_problems": None,
            "remediation_status": 123,
            "verification_status": {},
            "recent_activity": "invalid",
        },
    )

    assert dashboard.active_cases() == []
    assert dashboard.fleet_alerts() == []
    assert dashboard.unresolved_problems() == []
    assert dashboard.remediation_status() == []
    assert dashboard.verification_status() == []
    assert dashboard.recent_activity() == []


def test_v1_dashboard_to_dict_contains_all_operational_surfaces():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "active_cases": [{"case_id": "CASE-001"}],
            "fleet_alerts": [{"alert_id": "ALERT-001"}],
            "unresolved_problems": [{"problem_id": "P-001"}],
            "remediation_status": [{"action_id": "A-001"}],
            "verification_status": [{"action_id": "A-001"}],
            "recent_activity": [{"type": "CASE_UPDATED"}],
        },
    )

    data = dashboard.to_dict()

    assert "active_cases" in data
    assert "fleet_alerts" in data
    assert "unresolved_problems" in data
    assert "remediation_status" in data
    assert "verification_status" in data
    assert "recent_activity" in data


def test_v1_dashboard_remains_presentation_only():
    dashboard = DashboardViewModel(
        create_state()
    )

    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "recommend",
        "authorize",
        "execute",
        "remediate",
        "verify",
        "retry",
    }

    public_methods = {
        name
        for name in dir(dashboard)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)

def test_v1_dashboard_operational_surfaces_report_counts():
    dashboard = DashboardViewModel(
        create_state(),
        {
            "active_cases": [
                {},
                {},
            ],
            "fleet_alerts": [
                {},
            ],
            "unresolved_problems": [
                {},
                {},
                {},
            ],
            "remediation_status": [
                {},
            ],
            "verification_status": [
                {},
                {},
            ],
            "recent_activity": [
                {},
                {},
                {},
                {},
            ],
        },
    )

    assert len(dashboard.active_cases()) == 2
    assert len(dashboard.fleet_alerts()) == 1
    assert len(dashboard.unresolved_problems()) == 3
    assert len(dashboard.remediation_status()) == 1
    assert len(dashboard.verification_status()) == 2
    assert len(dashboard.recent_activity()) == 4
