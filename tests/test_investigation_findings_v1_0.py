from engine.cross_domain_diagnostic_reasoning import (
    CrossDomainDiagnosticReasoning,
)
from engine.diagnostic_case import DiagnosticCase
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
                    },
                    {
                        "finding": "HIGH_PROCESS_USAGE",
                        "severity": "HIGH",
                        "domain": "PROCESS",
                    },
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
        InvestigationFindings(None)
    except ValueError as exc:
        assert "DiagnosticInvestigationOrchestrator" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_extracts_structured_findings():
    findings = InvestigationFindings(make_orchestrator())

    result = findings.collect()

    assert result == [
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


def test_findings_are_defensive():
    findings = InvestigationFindings(make_orchestrator())

    result = findings.collect()

    result.append({"finding": "TAMPERED"})

    assert findings.findings() == [
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


def test_empty_investigation_produces_no_findings():
    workflow = TechnicianWorkflow(DiagnosticCase())

    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    orchestrator = DiagnosticInvestigationOrchestrator(
        workflow,
        investigation=Investigation(),
    )

    orchestrator.start()

    findings = InvestigationFindings(orchestrator)

    assert findings.collect() == []


def test_findings_projection_contains_case_identity():
    findings = InvestigationFindings(make_orchestrator())

    projection = findings.projection()

    assert projection["case_id"] == findings.orchestrator.case.case_id
    assert len(projection["findings"]) == 2


def test_does_not_mutate_diagnostic_case():
    orchestrator = make_orchestrator()

    original = list(orchestrator.case.findings)

    findings = InvestigationFindings(orchestrator)
    findings.collect()

    assert orchestrator.case.findings == original


def test_does_not_expose_remediation_processing():
    findings = InvestigationFindings(make_orchestrator())

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(findings)))
