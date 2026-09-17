from application.technician import Technician
from engine.diagnostic_case import DiagnosticCase


def test_technician_can_be_created():

    technician = Technician()

    assert technician is not None


def test_technician_has_diagnostic_engine():

    technician = Technician()

    assert technician.diagnostic_engine is not None


def test_technician_diagnose_returns_result():

    technician = Technician()

    result = technician.diagnose()

    assert isinstance(result, dict)


def test_technician_result_contains_evidence():

    technician = Technician()

    result = technician.diagnose()

    assert "evidence" in result


def test_technician_result_contains_diagnosis():

    technician = Technician()

    result = technician.diagnose()

    assert "diagnosis" in result

def test_technician_get_status_returns_valid_status():

    technician = Technician()

    status = technician.get_status()

    assert status in (
        "NORMAL",
        "INFO",
        "WARNING",
        "CRITICAL"
    )

def test_technician_get_primary_issue_returns_result():

    technician = Technician()

    primary_issue = technician.get_primary_issue()

    assert isinstance(
        primary_issue,
        dict
    )


def test_technician_get_primary_issue_contains_required_fields():

    technician = Technician()

    primary_issue = technician.get_primary_issue()

    assert "status" in primary_issue
    assert "category" in primary_issue
    assert "issue" in primary_issue
    assert "severity" in primary_issue
    assert "priority_score" in primary_issue
    assert "reason" in primary_issue

def test_technician_last_result_starts_empty():

    technician = Technician()

    assert technician.last_result is None


def test_technician_last_result_is_saved_after_diagnosis():

    technician = Technician()

    result = technician.diagnose()

    assert technician.last_result is result

def test_technician_get_report_returns_string():

    technician = Technician()

    report = technician.get_report()

    assert isinstance(report, str)


def test_technician_get_report_contains_diagnostic_information():

    technician = Technician()

    report = technician.get_report()

    assert len(report) > 0

def _technician_with_primary_root_cause(monkeypatch):

    technician = Technician()

    case = DiagnosticCase()

    case.primary_root_cause = {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9,
        "evidence": [
            "High memory usage detected"
        ]
    }

    case.recommendations = [
        {
            "category": "MEMORY",
            "recommendation": (
                "Investigate memory-consuming processes"
            )
        }
    ]

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    return technician


def test_technician_case_decision_contains_primary_root_cause(
    monkeypatch
):

    technician = _technician_with_primary_root_cause(
        monkeypatch
    )

    result = technician.diagnose()

    case_decision = result["case_decision"]

    assert "primary_root_cause" in case_decision


def test_technician_case_decision_contains_action(
    monkeypatch
):

    technician = _technician_with_primary_root_cause(
        monkeypatch
    )

    result = technician.diagnose()

    case_decision = result["case_decision"]

    assert "action" in case_decision


def test_technician_case_decision_contains_priority(
    monkeypatch
):

    technician = _technician_with_primary_root_cause(
        monkeypatch
    )

    result = technician.diagnose()

    case_decision = result["case_decision"]

    assert "priority" in case_decision


def test_technician_case_decision_contains_recommendation(
    monkeypatch
):

    technician = _technician_with_primary_root_cause(
        monkeypatch
    )

    result = technician.diagnose()

    case_decision = result["case_decision"]

    assert "recommendation" in case_decision


def test_technician_case_decision_contains_explanation(
    monkeypatch
):

    technician = _technician_with_primary_root_cause(
        monkeypatch
    )

    result = technician.diagnose()

    case_decision = result["case_decision"]

    assert "explanation" in case_decision

def test_technician_report_is_case_report():

    technician = Technician()

    technician.diagnose()

    report = technician.get_report()

    assert "Windows Technician v0.5" in report
    assert "DIAGNOSTIC CASE" in report

def test_technician_diagnostic_case_is_saved_with_result(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.evidence = {
        "CPU": {
            "usage_percent": 25.0
        }
    }

    case.findings = [
        {
            "category": "CPU",
            "severity": "INFO",
            "message": "CPU operating normally",
            "priority_score": 10
        }
    ]

    case.correlations = []

    case.root_causes = []

    case.root_cause_candidates = []

    case.primary_root_cause = None

    case.recommendations = []

    case.status = "NORMAL"

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "evidence": case.evidence,
            "diagnosis": {
                "status": "NORMAL",
                "total_findings": 1,
                "findings": case.findings,
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    result = technician.diagnose()

    assert "diagnostic_case" in result

    assert result["diagnostic_case"]["evidence"] == (
        case.evidence
    )

    assert result["diagnostic_case"]["findings"] == (
        case.findings
    )

    assert result["diagnostic_case"]["status"] == (
        case.status
    )


def test_technician_diagnostic_case_is_independent_copy(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.evidence = {
        "CPU": {
            "usage_percent": 25.0
        }
    }

    case.findings = []

    case.correlations = []
    case.root_causes = []
    case.root_cause_candidates = []
    case.primary_root_cause = None
    case.recommendations = []
    case.status = "NORMAL"

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "evidence": case.evidence,
            "diagnosis": {
                "status": "NORMAL",
                "total_findings": 0,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    result = technician.diagnose()

    diagnostic_case = result[
        "diagnostic_case"
    ]

    diagnostic_case["evidence"]["CPU"][
        "usage_percent"
    ] = 99.0

    assert case.evidence["CPU"][
        "usage_percent"
    ] == 25.0

def test_technician_case_decision_preserves_case_data(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.primary_root_cause = {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9
    }

    case.recommendations = [
        {
            "recommendation": "Investigate memory-consuming processes",
            "category": "MEMORY",
            "severity": "WARNING",
        }
    ]

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    result = technician.diagnose()

    decision = result[
        "case_decision"
    ]

    assert decision[
        "primary_root_cause"
    ] == case.primary_root_cause

    assert decision[
        "recommendation"
    ] == case.recommendations[0]


def test_technician_case_decision_is_independent_copy(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.primary_root_cause = {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9
    }

    case.recommendations = [
        {
            "recommendation": "Investigate memory-consuming processes",
            "category": "MEMORY",
            "severity": "WARNING",
        }
    ]

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    result = technician.diagnose()

    decision = result[
        "case_decision"
    ]

    decision[
        "primary_root_cause"
    ]["cause"] = "Modified cause"

    assert case.primary_root_cause[
        "cause"
    ] == "Memory pressure"

def test_technician_report_uses_current_diagnostic_case(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.status = "CRITICAL"

    case.primary_root_cause = {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9
    }

    case.recommendations = [
        {
            "recommendation": "Investigate memory-consuming processes",
            "category": "MEMORY",
            "severity": "WARNING",
        }
    ]
    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    technician.diagnose()

    captured_case = {}

    def fake_generate_case_report(received_case):

        captured_case["case"] = received_case

        return "Windows Technician v0.5\nDIAGNOSTIC CASE"

    monkeypatch.setattr(
        "application.technician.generate_case_report",
        fake_generate_case_report
    )

    report = technician.get_report()

    assert report == (
        "Windows Technician v0.5\n"
        "DIAGNOSTIC CASE"
    )

    assert captured_case["case"] is case

def test_technician_reuses_existing_diagnosis(
    monkeypatch
):

    technician = Technician()

    calls = {
        "count": 0
    }

    def fake_diagnose():

        calls["count"] += 1

        technician.last_result = {
            "diagnosis": {
                "status": "NORMAL",
                "findings": [],
                "recommendations": [],
                "total_findings": 0
            }
        }

        return technician.last_result

    monkeypatch.setattr(
        technician,
        "diagnose",
        fake_diagnose
    )

    technician.get_status()

    technician.get_primary_issue()

    technician.get_status()

    assert calls["count"] == 1

def test_technician_get_report_reuses_existing_diagnosis(
    monkeypatch
):

    technician = Technician()

    technician.last_result = {
        "evidence": {},
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 0,
            "findings": [],
            "recommendations": []
        },
        "diagnostic_case": {},
        "case_decision": {}
    }

    def fail_if_diagnose_called():

        raise AssertionError(
            "get_report() triggered a new diagnosis"
        )

    monkeypatch.setattr(
        technician,
        "diagnose",
        fail_if_diagnose_called
    )

    report = technician.get_report()

    assert isinstance(report, str)

def test_technician_case_decision_is_empty_without_primary_root_cause(
    monkeypatch
):

    technician = Technician()

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "evidence": {},
            "diagnosis": {
                "status": "NORMAL",
                "total_findings": 0,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: DiagnosticCase()
    )

    result = technician.diagnose()

    assert result["case_decision"] == {}

def test_technician_case_decision_reflects_current_root_cause(
    monkeypatch
):

    technician = Technician()

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "CPU overload",
            "severity": "MEDIUM",
            "confidence": 0.7
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "run",
        lambda: {
            "evidence": {},
            "diagnosis": {
                "status": "WARNING",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            }
        }
    )

    monkeypatch.setattr(
        technician.diagnostic_orchestrator,
        "get_case",
        lambda: case
    )

    result = technician.diagnose()

    decision = result["case_decision"]

    assert decision["cause"] == "CPU overload"
    assert decision["severity"] == "MEDIUM"
    assert decision["confidence"] == 0.7
    assert decision["action"] == "REVIEW_RECOMMENDED"
    assert decision["priority"] == "REVIEW"


