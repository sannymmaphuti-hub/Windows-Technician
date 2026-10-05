from engine.case_reporting import CaseReporting
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def create_case_and_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return case, workflow


def test_reporting_requires_workflow():
    try:
        CaseReporting(None)
    except ValueError:
        return

    raise AssertionError(
        "CaseReporting should reject None workflow."
    )


def test_reporting_requires_technician_workflow():
    try:
        CaseReporting(object())
    except ValueError:
        return

    raise AssertionError(
        "CaseReporting should require a TechnicianWorkflow."
    )


def test_reporting_exposes_case():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert report.case is case


def test_reporting_exposes_case_id():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert report.case_id == case.case_id


def test_reporting_exposes_machine_id():
    case, workflow = create_case_and_workflow()

    case.machine_id = "machine-001"

    report = CaseReporting(workflow)

    assert report.machine_id == "machine-001"


def test_reporting_exposes_hostname():
    case, workflow = create_case_and_workflow()

    case.hostname = "PC-001"

    report = CaseReporting(workflow)

    assert report.hostname == "PC-001"


def test_reporting_exposes_workflow_state():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert report.state == workflow.state


def test_reporting_exposes_workflow_history():
    case, workflow = create_case_and_workflow()

    workflow.start_investigation()

    report = CaseReporting(workflow)

    assert report.history == workflow.history


def test_reporting_exposes_findings():
    case, workflow = create_case_and_workflow()

    case.findings.append("Network instability")

    report = CaseReporting(workflow)

    assert report.findings == ["Network instability"]


def test_reporting_exposes_root_causes():
    case, workflow = create_case_and_workflow()

    case.root_causes.append("Network configuration issue")

    report = CaseReporting(workflow)

    assert report.root_causes == [
        "Network configuration issue"
    ]


def test_reporting_exposes_recommendations():
    case, workflow = create_case_and_workflow()

    case.recommendations.append("Review network configuration")

    report = CaseReporting(workflow)

    assert report.recommendations == [
        "Review network configuration"
    ]


def test_reporting_returns_summary():
    case, workflow = create_case_and_workflow()

    case.machine_id = "machine-001"
    case.hostname = "PC-001"

    report = CaseReporting(workflow)

    summary = report.summary

    assert isinstance(summary, dict)
    assert summary["case_id"] == case.case_id
    assert summary["machine_id"] == "machine-001"
    assert summary["hostname"] == "PC-001"
    assert summary["state"] == workflow.state


def test_reporting_summary_contains_history():
    case, workflow = create_case_and_workflow()

    workflow.start_investigation()

    report = CaseReporting(workflow)

    assert report.summary["history"] == workflow.history


def test_reporting_summary_contains_findings():
    case, workflow = create_case_and_workflow()

    case.findings.append("Test finding")

    report = CaseReporting(workflow)

    assert report.summary["findings"] == ["Test finding"]


def test_reporting_summary_contains_root_causes():
    case, workflow = create_case_and_workflow()

    case.root_causes.append("Test root cause")

    report = CaseReporting(workflow)

    assert report.summary["root_causes"] == [
        "Test root cause"
    ]


def test_reporting_summary_contains_recommendations():
    case, workflow = create_case_and_workflow()

    case.recommendations.append("Test recommendation")

    report = CaseReporting(workflow)

    assert report.summary["recommendations"] == [
        "Test recommendation"
    ]


def test_reporting_does_not_change_workflow_state():
    case, workflow = create_case_and_workflow()

    original_state = workflow.state

    report = CaseReporting(workflow)

    _ = report.summary

    assert workflow.state == original_state


def test_reporting_does_not_authorize_remediation():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert not hasattr(report, "authorize")


def test_reporting_does_not_execute_remediation():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert not hasattr(report, "execute")


def test_reporting_is_read_oriented():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert report.workflow is workflow
    assert report.case is case


def test_reporting_preserves_case_identity():
    case, workflow = create_case_and_workflow()

    report = CaseReporting(workflow)

    assert report.case_id == case.case_id