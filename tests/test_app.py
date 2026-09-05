# ==========================================
# Windows Technician v0.3
# APPLICATION TEST
# ==========================================

from application.app import TechnicianApp
from copy import deepcopy
from pathlib import Path
import pytest


def test_application_can_be_created():

    app = TechnicianApp()

    assert app is not None


def test_application_has_technician():

    app = TechnicianApp()

    assert app.technician is not None


def test_application_has_diagnostic_engine():

    app = TechnicianApp()

    assert app.technician.diagnostic_engine is not None


def test_application_diagnostics_returns_result():

    app = TechnicianApp()

    result = app.run_diagnostics()

    assert isinstance(result, dict)

    assert "evidence" in result
    assert "diagnosis" in result


def test_application_status_is_valid():

    app = TechnicianApp()

    status = app.get_status()

    assert status in (
        "NORMAL",
        "WARNING",
        "CRITICAL"
    )

def test_application_get_primary_issue_returns_result():

    app = TechnicianApp()

    primary_issue = app.get_primary_issue()

    assert isinstance(
        primary_issue,
        dict
    )


def test_application_get_primary_issue_contains_required_fields():

    app = TechnicianApp()

    primary_issue = app.get_primary_issue()

    assert "status" in primary_issue
    assert "category" in primary_issue
    assert "issue" in primary_issue
    assert "severity" in primary_issue
    assert "priority_score" in primary_issue
    assert "reason" in primary_issue

def test_application_primary_issue_has_valid_priority_score():

    app = TechnicianApp()

    primary_issue = app.get_primary_issue()

    assert isinstance(
        primary_issue["priority_score"],
        (int, float)
    )


def test_application_primary_issue_has_valid_severity():

    app = TechnicianApp()

    primary_issue = app.get_primary_issue()

    assert primary_issue["severity"] in (
        "INFO",
        "ATTENTION",
        "WARNING",
        "CRITICAL"
    )

def test_application_get_report_returns_string():

    app = TechnicianApp()

    report = app.get_report()

    assert isinstance(report, str)


def test_application_get_report_contains_diagnostic_information():

    app = TechnicianApp()

    report = app.get_report()

    assert len(report) > 0

def test_application_save_report_returns_path():

    app = TechnicianApp()

    path = app.save_report()

    assert isinstance(path, str)


def test_application_save_report_creates_file():

    app = TechnicianApp()

    path = app.save_report()

    from pathlib import Path

    assert Path(path).exists()

def test_application_diagnostics_contains_v03_diagnostic_case():

    app = TechnicianApp()

    result = app.run_diagnostics()

    assert "diagnostic_case" in result


def test_application_diagnostic_case_contains_v03_sections():

    app = TechnicianApp()

    result = app.run_diagnostics()

    case = result["diagnostic_case"]

    assert "evidence" in case
    assert "findings" in case
    assert "correlations" in case
    assert "root_cause_candidates" in case
    assert "primary_root_cause" in case
    assert "recommendations" in case
    assert "status" in case


def test_application_exposes_v03_primary_root_cause():

    app = TechnicianApp()

    result = app.run_diagnostics()

    case = result["diagnostic_case"]

    assert "primary_root_cause" in case


def test_application_exposes_v03_recommendations():

    app = TechnicianApp()

    result = app.run_diagnostics()

    case = result["diagnostic_case"]

    assert isinstance(
        case["recommendations"],
        list
    )

def test_application_report_is_v03_case_report():

    app = TechnicianApp()

    app.run_diagnostics()

    report = app.get_report()

    assert "WINDOWS TECHNICIAN v0.3" in report
    assert "DIAGNOSTIC CASE" in report


def test_application_save_report_saves_current_v03_report():

    app = TechnicianApp()

    app.run_diagnostics()

    path = app.save_report()

    from pathlib import Path

    report = Path(path).read_text(
        encoding="utf-8"
    )

    assert "WINDOWS TECHNICIAN v0.3" in report
    assert "DIAGNOSTIC CASE" in report

def test_application_save_report_matches_current_report(
    monkeypatch,
    tmp_path
):

    app = TechnicianApp()

    expected_report = (
        "WINDOWS TECHNICIAN v0.3\n"
        "DIAGNOSTIC CASE\n"
        "TEST REPORT"
    )

    monkeypatch.setattr(
        app,
        "get_report",
        lambda: expected_report
    )

    monkeypatch.chdir(tmp_path)

    path = app.save_report()

    from pathlib import Path

    saved_report = Path(path).read_text(
        encoding="utf-8"
    )

    assert saved_report == expected_report

def test_application_run_diagnostics_creates_new_diagnosis():

    app = TechnicianApp()

    first_result = app.run_diagnostics()

    technician = app.technician

    first_stored_result = technician.last_result

    second_result = app.run_diagnostics()

    second_stored_result = technician.last_result

    assert second_result is not first_result
    assert second_stored_result is not first_stored_result
    assert second_stored_result is not first_result
    assert second_stored_result == second_result

def test_application_diagnostic_case_is_exposed_from_technician(
    monkeypatch
):

    app = TechnicianApp()

    expected_case = {
        "evidence": [],
        "findings": [],
        "correlations": [],
        "root_cause_candidates": [],
        "primary_root_cause": None,
        "recommendations": [],
        "status": "NORMAL"
    }

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        lambda: {
            "evidence": [],
            "diagnosis": {
                "status": "NORMAL",
                "total_findings": 0,
                "findings": [],
                "recommendations": []
            },
            "diagnostic_case": expected_case,
            "case_decision": {}
        }
    )

    result = app.run_diagnostics()

    assert result["diagnostic_case"] == expected_case

def test_application_exposes_case_decision(
    monkeypatch
):

    app = TechnicianApp()

    expected_decision = {
        "primary_root_cause": {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        },
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9,
        "action": "IMMEDIATE_ATTENTION",
        "priority": "CRITICAL",
        "recommendation": (
            "Investigate memory-consuming processes"
        ),
        "explanation": (
            "Memory pressure was identified with HIGH severity "
            "and 90% confidence. Immediate attention is required."
        )
    }

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        lambda: {
            "evidence": [],
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": [],
                "recommendations": []
            },
            "diagnostic_case": {},
            "case_decision": expected_decision
        }
    )

    result = app.run_diagnostics()

    assert result["case_decision"] == expected_decision

def test_application_get_status_reuses_existing_diagnosis(
    monkeypatch
):

    app = TechnicianApp()

    existing_result = {
        "evidence": [],
        "diagnosis": {
            "status": "CRITICAL",
            "total_findings": 1,
            "findings": [],
            "recommendations": []
        },
        "diagnostic_case": {},
        "case_decision": {}
    }

    app.technician.last_result = existing_result

    def fail_if_diagnose_called():

        raise AssertionError(
            "get_status() triggered a new diagnosis"
        )

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        fail_if_diagnose_called
    )

    status = app.get_status()

    assert status == "CRITICAL"

def test_application_get_primary_issue_reuses_existing_diagnosis(
    monkeypatch
):

    app = TechnicianApp()

    existing_result = {
        "evidence": [],
        "diagnosis": {
            "status": "CRITICAL",
            "total_findings": 1,
            "findings": [
                {
                    "category": "MEMORY",
                    "issue": "High memory usage",
                    "severity": "CRITICAL",
                    "priority_score": 95,
                    "reason": "Memory usage is critically high."
                }
            ],
            "recommendations": []
        },
        "diagnostic_case": {},
        "case_decision": {}
    }

    app.technician.last_result = existing_result

    def fail_if_diagnose_called():

        raise AssertionError(
            "get_primary_issue() triggered a new diagnosis"
        )

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        fail_if_diagnose_called
    )

    primary_issue = app.get_primary_issue()

    assert primary_issue["category"] == "MEMORY"
    assert primary_issue["issue"] == "High memory usage"
    assert primary_issue["severity"] == "CRITICAL"
    assert primary_issue["priority_score"] == 95

def test_application_get_report_reuses_existing_diagnosis(
    monkeypatch
):

    app = TechnicianApp()

    app.technician.last_result = {
        "evidence": [],
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
        app.technician,
        "diagnose",
        fail_if_diagnose_called
    )

    report = app.get_report()

    assert isinstance(report, str)

def test_application_preserves_diagnostic_case_and_case_decision(
    monkeypatch
):

    app = TechnicianApp()

    expected_case = {
        "evidence": ["memory usage evidence"],
        "findings": ["memory finding"],
        "correlations": ["memory-process correlation"],
        "root_cause_candidates": ["memory pressure"],
        "primary_root_cause": {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        },
        "recommendations": [
            "Investigate memory-consuming processes"
        ],
        "status": "CRITICAL"
    }

    expected_decision = {
        "primary_root_cause": expected_case[
            "primary_root_cause"
        ],
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9,
        "action": "IMMEDIATE_ATTENTION",
        "priority": "CRITICAL",
        "recommendation": (
            "Investigate memory-consuming processes"
        )
    }

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        lambda: {
            "evidence": expected_case["evidence"],
            "diagnosis": {
                "status": "CRITICAL",
                "total_findings": 1,
                "findings": expected_case["findings"],
                "recommendations": expected_case[
                    "recommendations"
                ]
            },
            "diagnostic_case": expected_case,
            "case_decision": expected_decision
        }
    )

    result = app.run_diagnostics()

    assert result["diagnostic_case"] == expected_case
    assert result["case_decision"] == expected_decision

def test_application_case_decision_reflects_current_root_cause():

    app = TechnicianApp()

    result = app.run_diagnostics()

    case = result["diagnostic_case"]
    decision = result["case_decision"]

    if case["primary_root_cause"] is None:

        assert decision == {}

    else:

        assert decision["primary_root_cause"] == (
            case["primary_root_cause"]
        )

def test_application_case_decision_preserves_decision_fields():

    app = TechnicianApp()

    result = app.run_diagnostics()

    decision = result["case_decision"]

    if decision:

        assert "action" in decision
        assert "priority" in decision
        assert "recommendation" in decision
        assert "explanation" in decision

def test_application_case_decision_matches_current_case():

    app = TechnicianApp()

    result = app.run_diagnostics()

    case = result["diagnostic_case"]
    decision = result["case_decision"]

    if case["primary_root_cause"] is None:

        assert decision == {}

    else:

        assert decision["primary_root_cause"] == (
            case["primary_root_cause"]
        )

        assert decision["cause"] == (
            case["primary_root_cause"]["cause"]
        )

        assert decision["severity"] == (
            case["primary_root_cause"]["severity"]
        )

        assert decision["confidence"] == (
            case["primary_root_cause"].get("confidence")
        )

def test_application_new_diagnosis_replaces_previous_result():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    second_result = app.run_diagnostics()

    assert second_result is not first_result

    assert "diagnostic_case" in second_result
    assert "case_decision" in second_result

def test_application_diagnosis_results_are_independent():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    second_result = app.run_diagnostics()

    first_case = first_result["diagnostic_case"]
    second_case = second_result["diagnostic_case"]

    assert first_case is not second_case

def test_application_diagnosis_results_do_not_share_case_data():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    second_result = app.run_diagnostics()

    first_case = first_result["diagnostic_case"]
    second_case = second_result["diagnostic_case"]

    original_second_evidence = second_case["evidence"]

    first_case["evidence"] = {
        "TEST_MUTATION": "modified"
    }

    assert second_case["evidence"] == original_second_evidence

def test_application_diagnosis_results_do_not_share_case_decision():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    second_result = app.run_diagnostics()

    first_decision = first_result["case_decision"]
    second_decision = second_result["case_decision"]

    if not first_decision or not second_decision:
        return

    original_second_action = second_decision["action"]

    first_decision["action"] = "TEST_MUTATION"

    assert second_decision["action"] == original_second_action

def test_application_report_matches_current_diagnostic_state():

    app = TechnicianApp()

    result = app.run_diagnostics()

    report = app.get_report()

    assert isinstance(report, str)
    assert len(report) > 0

    assert "WINDOWS TECHNICIAN v0.3" in report
    assert "DIAGNOSTIC CASE" in report

    case = result["diagnostic_case"]

    if case["primary_root_cause"] is not None:

        cause = case["primary_root_cause"].get(
            "cause"
        )

        if cause:
            assert cause in report

def test_application_report_is_stable_for_existing_diagnosis():

    app = TechnicianApp()

    app.run_diagnostics()

    first_report = app.get_report()
    second_report = app.get_report()

    assert first_report == second_report

def test_application_new_diagnosis_updates_report_state():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    first_report = app.get_report()

    second_result = app.run_diagnostics()
    second_report = app.get_report()

    assert first_result is not second_result

    assert isinstance(first_report, str)
    assert isinstance(second_report, str)

    assert len(first_report) > 0
    assert len(second_report) > 0

def test_application_save_report_matches_current_diagnostic_state():

    app = TechnicianApp()

    result = app.run_diagnostics()

    current_report = app.get_report()

    path = app.save_report()

    from pathlib import Path

    saved_report = Path(path).read_text(
        encoding="utf-8"
    )

    assert saved_report == current_report

    assert "WINDOWS TECHNICIAN v0.3" in saved_report
    assert "DIAGNOSTIC CASE" in saved_report

    assert result["diagnostic_case"] is not None

def test_application_save_report_reuses_existing_diagnosis():

    app = TechnicianApp()

    app.run_diagnostics()

    original_result = app.technician.last_result

    app.save_report()

    assert app.technician.last_result is original_result

def test_application_save_report_does_not_modify_diagnostic_result():

    app = TechnicianApp()

    result = app.run_diagnostics()

    original_result = deepcopy(result)

    app.save_report()

    assert result == original_result

def test_application_saved_report_content_matches_current_report():

    app = TechnicianApp()

    app.run_diagnostics()

    current_report = app.get_report()

    report_path = app.save_report()

    saved_report = Path(report_path).read_text(
        encoding="utf-8"
    )

    assert saved_report == current_report

def test_application_new_diagnosis_updates_saved_report():

    app = TechnicianApp()

    first_result = app.run_diagnostics()
    first_report = app.get_report()

    second_result = app.run_diagnostics()
    second_report = app.get_report()

    report_path = app.save_report()

    saved_report = Path(report_path).read_text(
        encoding="utf-8"
    )

    assert second_result is not first_result
    assert second_report == saved_report

def test_application_save_report_returns_existing_file():

    app = TechnicianApp()

    app.run_diagnostics()

    report_path = app.save_report()

    assert Path(report_path).exists()
    assert Path(report_path).is_file()

def test_technician_app_starts_ready():
    app = TechnicianApp()

    assert app.get_execution_state() == "READY"


def test_technician_app_enters_running_state_during_diagnostics(monkeypatch):
    app = TechnicianApp()
    states = []

    original_diagnose = app.technician.diagnose

    def tracked_diagnose():
        states.append(app.get_execution_state())
        return original_diagnose()

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        tracked_diagnose
    )

    app.run_diagnostics()

    assert states == ["RUNNING"]


def test_technician_app_completes_after_successful_diagnostics():
    app = TechnicianApp()

    app.run_diagnostics()

    assert app.get_execution_state() == "COMPLETED"

def test_technician_app_enters_error_state_when_diagnostics_fail(monkeypatch):
    app = TechnicianApp()

    def failing_diagnose():
        raise RuntimeError("Diagnostic failure")

    monkeypatch.setattr(
        app.technician,
        "diagnose",
        failing_diagnose
    )

    with pytest.raises(RuntimeError, match="Diagnostic failure"):
        app.run_diagnostics()

    assert app.get_execution_state() == "ERROR"

def test_technician_app_exposes_dashboard_view_model():
    app = TechnicianApp()

    app.run_diagnostics()

    model = app.get_dashboard_view_model()

    assert model is not None


def test_technician_app_dashboard_view_model_contains_execution_state():
    app = TechnicianApp()

    app.run_diagnostics()

    model = app.get_dashboard_view_model()

    assert model.execution_state == "COMPLETED"
    assert model.execution_label == "Diagnostics Complete"


def test_technician_app_dashboard_view_model_contains_diagnostic_status():
    app = TechnicianApp()

    app.run_diagnostics()

    model = app.get_dashboard_view_model()

    assert model.status == app.get_status()
