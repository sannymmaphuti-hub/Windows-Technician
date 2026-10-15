from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_investigation_case_integration import (
    DiagnosticInvestigationCaseIntegration,
)
from engine.diagnostic_investigation_orchestrator import (
    DiagnosticInvestigationOrchestrator,
)
from engine.investigation_findings import InvestigationFindings
from engine.technician_workflow import TechnicianWorkflow


def make_orchestrator():
    workflow = TechnicianWorkflow(DiagnosticCase())

    class Investigation:
        def investigate(self, system_data=None):
            return {
                "findings": [
                    {
                        "finding": "HIGH_MEMORY_USAGE",
                        "severity": "HIGH",
                        "domain": "MEMORY",
                    }
                ]
            }

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    return orchestrator


def test_requires_canonical_orchestrator():
    try:
        DiagnosticInvestigationCaseIntegration(None)
    except ValueError as exc:
        assert "DiagnosticInvestigationOrchestrator" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_uses_canonical_investigation_findings():
    orchestrator = make_orchestrator()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    assert isinstance(
        integration.findings,
        InvestigationFindings,
    )


def test_integrates_findings_into_diagnostic_case():
    orchestrator = make_orchestrator()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    result = integration.integrate_findings()

    assert result == [
        {
            "finding": "HIGH_MEMORY_USAGE",
            "severity": "HIGH",
            "domain": "MEMORY",
        }
    ]

    assert orchestrator.case.findings == result


def test_integration_uses_canonical_set_findings_api():
    orchestrator = make_orchestrator()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    findings = [
        {
            "finding": "CANONICAL_FINDING",
            "severity": "HIGH",
            "domain": "MEMORY",
        }
    ]

    orchestrator.case.set_findings(findings)

    assert orchestrator.case.findings == findings


def test_integrated_findings_are_defensive():
    orchestrator = make_orchestrator()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    result = integration.integrate_findings()

    result.append({"finding": "TAMPERED"})

    assert orchestrator.case.findings == [
        {
            "finding": "HIGH_MEMORY_USAGE",
            "severity": "HIGH",
            "domain": "MEMORY",
        }
    ]


def test_projection_contains_canonical_case_findings():
    orchestrator = make_orchestrator()

    integration = DiagnosticInvestigationCaseIntegration(
        orchestrator
    )

    integration.integrate_findings()

    projection = integration.projection()

    assert projection == {
        "case_id": orchestrator.case.case_id,
        "findings": [
            {
                "finding": "HIGH_MEMORY_USAGE",
                "severity": "HIGH",
                "domain": "MEMORY",
            }
        ],
    }


def test_does_not_expose_remediation_processing():
    integration = DiagnosticInvestigationCaseIntegration(
        make_orchestrator()
    )

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(integration)))
