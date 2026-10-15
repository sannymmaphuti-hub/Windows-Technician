import pytest

from ui.dashboard_information_model import (
    DashboardFinding,
    DashboardInformationModel,
)


def test_dashboard_prioritizes_findings_requiring_attention():
    model = DashboardInformationModel()
    findings = [
        DashboardFinding("Memory", "warning", "Memory usage is elevated.", True),
        DashboardFinding("Disk", "healthy", "Disk health is normal."),
        DashboardFinding("Startup", "info", "Startup was reviewed.", True),
    ]

    result = model.build(
        system_name="Workstation",
        health_status="Needs attention",
        findings=findings,
    )

    assert result["health"]["finding_count"] == 3
    assert result["health"]["attention_count"] == 2
    assert [item["title"] for item in result["priority_findings"]] == [
        "Memory",
        "Startup",
    ]


def test_dashboard_preserves_supplied_health_and_activity():
    result = DashboardInformationModel().build(
        system_name="Office PC",
        health_status="Unknown",
        findings=[],
        activity="Waiting for authorization",
    )

    assert result["health"]["status"] == "Unknown"
    assert result["activity"]["status"] == "Waiting for authorization"


def test_dashboard_does_not_execute_diagnostics_or_remediation():
    result = DashboardInformationModel().build(
        system_name="Test PC",
        health_status="Unknown",
        findings=[],
    )

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False


def test_dashboard_projection_is_detached():
    result = DashboardInformationModel().build(
        system_name="Test PC",
        health_status="Warning",
        findings=[
            DashboardFinding("Memory", "warning", "High usage.", True)
        ],
        next_steps=["Review memory usage"],
    )

    result["findings"][0]["title"] = "Changed"
    result["next_steps"].append("Injected step")

    fresh = DashboardInformationModel().build(
        system_name="Test PC",
        health_status="Warning",
        findings=[
            DashboardFinding("Memory", "warning", "High usage.", True)
        ],
        next_steps=["Review memory usage"],
    )

    assert fresh["findings"][0]["title"] == "Memory"
    assert fresh["next_steps"] == ["Review memory usage"]


@pytest.mark.parametrize("name", ["", "   "])
def test_dashboard_rejects_empty_system_name(name):
    with pytest.raises(ValueError):
        DashboardInformationModel().build(
            system_name=name,
            health_status="Unknown",
            findings=[],
        )


def test_dashboard_rejects_invalid_finding_type():
    with pytest.raises(TypeError):
        DashboardInformationModel().build(
            system_name="Test PC",
            health_status="Unknown",
            findings=[{"title": "Memory"}],
        )


def test_dashboard_rejects_invalid_next_steps():
    with pytest.raises(ValueError):
        DashboardInformationModel().build(
            system_name="Test PC",
            health_status="Unknown",
            findings=[],
            next_steps=["Review memory", ""],
        )
