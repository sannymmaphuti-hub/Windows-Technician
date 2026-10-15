from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_case_integration import (
    DiagnosticInvestigationCaseIntegration,
)
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.investigation_findings import InvestigationFindings
from engine.technician_investigation_workspace import (
    TechnicianInvestigationWorkspace,
)
from engine.technician_workflow import TechnicianWorkflow


def make_workspace():
    workflow = TechnicianWorkflow(DiagnosticCase())

    class Investigation:
        def investigate(self, system_data=None):
            return {
                "findings": [
                    {
                        "finding": "HIGH_MEMORY_USAGE",
                        "severity": "HIGH",
                        "domain": "MEMORY",
                    },
                    {
                        "finding": "HIGH_PROCESS_USAGE",
                        "severity": "HIGH",
                        "domain": "PROCESS",
                    },
                ],
                "status": "INVESTIGATED",
            }

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    integration.integrate_findings()

    return TechnicianInvestigationWorkspace(
        orchestrator=orchestrator,
        findings=InvestigationFindings(orchestrator),
    )


def test_requires_canonical_orchestrator():
    try:
        TechnicianInvestigationWorkspace(None)
    except ValueError as exc:
        assert "DiagnosticInvestigationOrchestrator" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_uses_canonical_investigation_findings():
    workspace = make_workspace()

    assert isinstance(
        workspace.findings,
        InvestigationFindings,
    )


def test_investigation_state_is_projected():
    workspace = make_workspace()

    assert workspace.investigation_state == "COMPLETED"


def test_findings_are_projected():
    workspace = make_workspace()

    assert workspace.findings_projection() == [
        {
            "finding": "HIGH_MEMORY_USAGE",
            "severity": "HIGH",
            "domain": "MEMORY",
        },
        {
            "finding": "HIGH_PROCESS_USAGE",
            "severity": "HIGH",
            "domain": "PROCESS",
        },
    ]


def test_workspace_projection_contains_case_identity():
    workspace = make_workspace()

    projection = workspace.projection()

    assert projection["case_id"] == workspace.case.case_id
    assert projection["investigation_state"] == "COMPLETED"
    assert len(projection["findings"]) == 2


def test_workspace_is_read_only_investigation_surface():
    workspace = make_workspace()

    forbidden = {
        "investigate",
        "analyze",
        "authorize",
        "execute",
        "remediate",
        "verify",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(workspace)))


def test_workspace_does_not_create_another_case():
    workspace = make_workspace()

    assert workspace.case is workspace.orchestrator.case


def test_workspace_findings_are_defensive():
    workspace = make_workspace()

    findings = workspace.findings_projection()
    findings.append({"finding": "TAMPERED"})

    assert len(workspace.findings_projection()) == 2


def test_workspace_projection_is_defensive():
    workspace = make_workspace()

    projection = workspace.projection()

    projection["findings"].append(
        {"finding": "TAMPERED"}
    )

    assert len(workspace.projection()["findings"]) == 2
