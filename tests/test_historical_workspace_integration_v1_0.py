from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_intelligence_integration import (
    HistoricalIntelligenceIntegration,
)
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)
from engine.system_wide_intelligence_projection import (
    SystemWideIntelligenceProjection,
)
from engine.technician_investigation_workspace import (
    TechnicianInvestigationWorkspace,
)
from engine.technician_workspace import TechnicianWorkspace
from engine.technician_workflow import TechnicianWorkflow


def make_case(
    machine_id="machine-1",
    findings=None,
):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = "TEST-PC"
    case.observations = []
    case.signals = []
    case.correlations = []
    case.findings = findings or []
    return case


def make_history():
    history = DiagnosticHistory()
    history.record_case(
        make_case(
            findings=[{"finding": "HIGH_MEMORY", "severity": "HIGH"}]
        )
    )
    history.record_case(
        make_case(
            findings=[{"finding": "HIGH_MEMORY", "severity": "HIGH"}]
        )
    )
    return history

def make_projection():
    case = make_case(
        findings=[
            {
                "finding": "CPU_PRESSURE",
                "severity": "WARNING",
            }
        ]
    )

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    return SystemWideIntelligenceProjection(
        integration
    )


def make_workspace():
    case = make_case(
        findings=[
            {
                "finding": "CPU_PRESSURE",
                "severity": "WARNING",
            }
        ]
    )

    workflow = TechnicianWorkflow(case)

    projection = SystemWideIntelligenceProjection(
        SystemWideIntelligenceIntegration(
            case,
            historical=HistoricalIntelligenceIntegration(
                make_history()
            ),
        )
    )

    return TechnicianWorkspace(
        workflow,
        intelligence=projection,
    )


def test_projection_exposes_historical_intelligence():
    projection = make_projection()

    historical = projection.historical()

    assert historical["machine_id"] == "machine-1"
    assert "trend" in historical
    assert "recurrence" in historical
    assert "baseline" in historical
    assert "deviation" in historical


def test_projection_intelligence_contains_historical_surface():
    projection = make_projection()

    intelligence = projection.intelligence()

    assert "historical" in intelligence


def test_projection_full_surface_contains_historical_intelligence():
    projection = make_projection()

    result = projection.projection()

    assert "case" in result
    assert "intelligence" in result
    assert "historical" in result["intelligence"]


def test_historical_projection_is_defensive():
    projection = make_projection()

    historical = projection.historical()

    historical["trend"]["findings"].append(
        {"finding": "TAMPERED"}
    )

    fresh = projection.historical()

    assert len(fresh["trend"]["findings"]) == 2


def test_workspace_exposes_historical_intelligence():
    workspace = make_workspace()

    historical = workspace.historical_intelligence()

    assert historical["machine_id"] == "machine-1"
    assert historical["deviation"]["is_deviation"] is True


def test_workspace_intelligence_projection_contains_history():
    workspace = make_workspace()

    intelligence = workspace.intelligence_projection()

    assert "historical" in intelligence


def test_workspace_full_projection_contains_history():
    workspace = make_workspace()

    projection = workspace.projection()

    assert "intelligence" in projection
    assert "historical" in projection["intelligence"]


def test_workspace_does_not_process_historical_intelligence():
    workspace = make_workspace()

    forbidden = {
        "investigate",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert forbidden.isdisjoint(set(dir(workspace)))


def test_projection_does_not_process_historical_intelligence():
    projection = make_projection()

    forbidden = {
        "investigate",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert forbidden.isdisjoint(set(dir(projection)))
