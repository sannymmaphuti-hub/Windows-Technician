# ==========================================
# Windows Technician v0.3
# APPLICATION TEST
# ==========================================

from application.app import TechnicianApp
from application.technician import Technician
from copy import deepcopy
from pathlib import Path
import pytest
from engine.remediation_action import RemediationAction


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

def test_diagnose_includes_remediation_actions():
    technician = Technician()

    result = technician.diagnose()

    assert "remediation_actions" in result
    assert isinstance(
        result["remediation_actions"],
        list
    )

def test_technician_has_remediation_coordinator():
    technician = Technician()

    assert technician.remediation_coordinator is not None

def test_diagnose_does_not_execute_remediation_actions():
    technician = Technician()

    result = technician.diagnose()

    for action in result["remediation_actions"]:
        assert action.authorization_status == "UNAUTHORIZED"
        assert action.execution_status == "NOT_EXECUTED"

def test_technician_can_execute_authorized_remediation():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = technician.remediation_coordinator.execute(action)

    assert result.action_id == "memory_review"
    assert result.execution_status == "EXECUTED"

def test_technician_can_remediate_authorized_action():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    action.authorize()

    result = technician.remediate(action)

    assert result.action_id == "memory_review"
    assert result.execution_status == "EXECUTED"

def test_technician_cannot_remediate_unauthorized_action():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    result = technician.remediate(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert action.authorization_status == "UNAUTHORIZED"

def test_technician_can_authorize_remediation_action():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    assert action.authorization_status == "UNAUTHORIZED"

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_technician_authorization_does_not_execute_remediation():
    technician = Technician()
    executions = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

def test_technician_authorize_then_remediate():
    technician = Technician()
    executions = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )

    technician.authorize_remediation(action)

    result = technician.remediate(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"
    assert executions == ["run"]

    assert result.action_id == "memory_review"
    assert result.execution_status == "EXECUTED"

def test_technician_remediate_can_verify_result():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected="memory_normal",
        observed="memory_normal",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result is not None
    assert result.verification_result["verified"] is True
    assert result.verification_result["action_id"] == "memory_review"

def test_technician_remediate_can_record_failed_verification():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: None,
    )

    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected="memory_normal",
        observed="memory_high",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result is not None
    assert result.verification_result["verified"] is False
    assert result.verification_result["action_id"] == "memory_review"

def test_technician_failed_remediation_is_not_verified():
    technician = Technician()

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: (_ for _ in ()).throw(
            RuntimeError("remediation failed")
        ),
    )

    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected="memory_normal",
        observed="memory_normal",
    )

    assert result.execution_status == "FAILED"
    assert result.verification_result is None

def test_technician_remediate_unauthorized_action_does_not_execute():
    technician = Technician()
    executions = []

    action = RemediationAction(
        action_id="memory_review",
        description="Review memory-intensive processes.",
        operation=lambda: executions.append("run"),
    )

    result = technician.remediate(action)

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert executions == []

    assert result.action_id == "memory_review"
    assert result.execution_status == "NOT_EXECUTED"
    assert result.verification_result is None

def test_diagnose_remediation_actions_are_unexecuted():
    technician = Technician()

    result = technician.diagnose()

    for action in result["remediation_actions"]:
        assert action.authorization_status == "UNAUTHORIZED"
        assert action.execution_status == "NOT_EXECUTED"

def test_diagnose_remediation_actions_preserve_context():
    technician = Technician()

    result = technician.diagnose()

    for action in result["remediation_actions"]:
        assert action.action_id
        assert action.description
        assert action.category is not None
        assert action.severity in {"WARNING", "CRITICAL"}

def test_technician_complete_remediation_workflow():
    technician = Technician()

    diagnosis = technician.diagnose()

    actions = diagnosis["remediation_actions"]

    if not actions:
        pytest.skip("No remediation actions available from current diagnosis.")

    action = actions[0]

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    result = technician.remediate(action)

    assert result.action_id == action.action_id
    assert result.execution_status == "NOT_EXECUTED"

def test_diagnose_remediation_actions_have_no_implicit_operation():
    technician = Technician()

    result = technician.diagnose()

    for action in result["remediation_actions"]:
        assert action.operation is None

def test_technician_has_remediation_operation_binder():
    technician = Technician()

    assert technician.remediation_operation_binder is not None

def test_technician_can_bind_registered_remediation_operation():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    assert action.operation is operation

def test_technician_can_bind_operation_to_planned_action():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    assert len(actions) == 1
    assert actions[0].operation is None

    technician.remediation_operation_binder.bind(
        action=actions[0],
        operation_id="test_operation",
    )

    assert actions[0].operation is operation

def test_technician_rejects_unregistered_operation_for_planned_action():
    technician = Technician()

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    assert len(actions) == 1
    assert actions[0].operation is None

    with pytest.raises(ValueError):
        technician.remediation_operation_binder.bind(
            action=actions[0],
            operation_id="unknown_operation",
        )

    assert actions[0].operation is None

def test_technician_can_execute_bound_and_authorized_planned_action():
    technician = Technician()

    state = {
        "executed": False,
    }

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    assert len(actions) == 1

    action = actions[0]

    assert action.operation is None
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    assert action.operation is operation
    assert state["executed"] is False

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert state["executed"] is False

    result = technician.remediate(action)

    assert result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"
    assert state["executed"] is True

def test_technician_can_record_failed_verification_for_bound_remediation():
    technician = Technician()

    state = {
        "memory_reviewed": False,
    }

    def operation():
        state["memory_reviewed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    action = actions[0]

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    technician.authorize_remediation(action)

    result = technician.remediate(action)

    assert result.execution_status == "EXECUTED"
    assert state["memory_reviewed"] is True

    verification = technician.remediation_coordinator.verifier.verify(
        expected=False,
        observed=state["memory_reviewed"],
        action_id=action.action_id,
    )

    result.verification_result = verification

    assert result.verification_result is not None
    assert result.verification_result["verified"] is False

def test_technician_does_not_verify_failed_bound_remediation():
    technician = Technician()

    def failing_operation():
        raise RuntimeError("simulated remediation failure")

    technician.remediation_operation_registry.register(
        "test_operation",
        failing_operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    action = actions[0]

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected=True,
        observed=True,
    )

    assert result.execution_status == "FAILED"
    assert result.verification_result is None

def test_technician_cannot_execute_bound_operation_without_authorization():
    technician = Technician()

    state = {
        "executed": False,
    }

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    action = actions[0]

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    assert action.operation is operation
    assert action.authorization_status == "UNAUTHORIZED"

    result = technician.remediate(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert action.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

def test_technician_cannot_execute_denied_bound_operation():
    technician = Technician()

    state = {
        "executed": False,
    }

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    recommendation = {
        "category": "MEMORY",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    actions = technician.remediation_action_planner.create_actions(
        [recommendation]
    )

    action = actions[0]

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    action.deny()

    assert action.authorization_status == "DENIED"

    result = technician.remediate(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert action.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

def test_binding_preserves_existing_authorization():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.operation is None

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    assert action.operation is operation
    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_binding_preserves_existing_execution_status():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        requires_authorization=False,
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    technician.remediate(action)

    assert action.execution_status == "EXECUTED"

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation"
    )

    assert action.operation is operation
    assert action.execution_status == "EXECUTED"

def test_binding_rejects_missing_action():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    with pytest.raises(ValueError, match="action is required"):
        technician.remediation_operation_binder.bind(
            action=None,
            operation_id="test_operation",
        )

def test_binding_rejects_missing_operation_id():
    technician = Technician()

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    with pytest.raises(ValueError, match="operation_id is required"):
        technician.remediation_operation_binder.bind(
            action=action,
            operation_id=None,
        )

def test_binding_rejects_rebinding_existing_operation():
    technician = Technician()

    first_operation = lambda: None
    second_operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        first_operation,
    )

    technician.remediation_operation_registry.register(
        "second_operation",
        second_operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    with pytest.raises(
        ValueError,
        match="operation already bound",
    ):
        technician.remediation_operation_binder.bind(
            action=action,
            operation_id="second_operation",
        )

    assert action.operation is first_operation
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_binding_preserves_denied_authorization():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    action.deny()

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    assert action.operation is operation
    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"

def test_binding_preserves_authorized_state():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.authorize_remediation(action)

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    assert action.operation is operation
    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_technician_can_bind_registered_operation_to_planned_action():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    assert action.operation is operation
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_technician_can_bind_authorize_and_execute_planned_action():
    technician = Technician()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

    result = technician.remediate(action)

    assert result is not None
    assert state["executed"] is True
    assert action.execution_status == "EXECUTED"

def test_technician_can_verify_bound_remediation_result():
    technician = Technician()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
    )

    technician.remediation_operation_binder.bind(
        action=action,
        operation_id="test_operation",
    )

    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert action.execution_status == "EXECUTED"
    assert state["executed"] is True

    assert result.verification_result["verified"] is True
    assert result.verification_result["action_id"] == "action_001"
    assert result.verification_result["expected"] == "healthy"
    assert result.verification_result["observed"] == "healthy"

def test_diagnose_remediation_actions_are_unbound_by_default():
    technician = Technician()

    result = technician.diagnose()

    actions = result["remediation_actions"]

    assert actions

    for action in actions:
        assert action.operation is None
        assert action.execution_status == "NOT_EXECUTED"
        assert action.authorization_status == "UNAUTHORIZED"

def test_technician_can_select_remediation_operation():
    technician = Technician()

    action = RemediationAction(
        action_id="action_001",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    operation_id = technician.select_remediation_operation(action)

    assert operation_id == "memory_review"


def test_technician_can_bind_selected_remediation_operation():
    technician = Technician()

    action = RemediationAction(
        action_id="action_002",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    assert action.operation is (
        technician.remediation_operation_registry.get(
            "memory_review"
        )
    )


def test_technician_does_not_bind_unsupported_remediation_operation():
    technician = Technician()

    action = RemediationAction(
        action_id="action_003",
        description="Investigate CPU usage.",
        category="CPU",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    assert action.operation is None


def test_technician_binding_does_not_execute_or_authorize():
    technician = Technician()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_004",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    assert action.operation is (
    technician.remediation_operation_registry.get(
        "memory_review"
    )
    )
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

def test_technician_complete_bound_remediation_workflow():
    technician = Technician()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_005",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    assert action.operation is (
        technician.remediation_operation_registry.get(
            "memory_review"
        )
    )

    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    result = technician.remediate(action)

    assert result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"
    assert action.operation.execution_status == "EXECUTED"

def test_technician_bound_action_can_be_verified():
    technician = Technician()

    operation = lambda: None

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_006",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)
    technician.authorize_remediation(action)

    result = technician.remediate(
        action,
        expected="healthy",
        observed="healthy",
    )

    assert result.execution_status == "EXECUTED"
    assert result.verification_result["verified"] is True


def test_technician_cannot_execute_bound_action_without_authorization():
    technician = Technician()

    state = {"executed": False}

    def operation():
        state["executed"] = True

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="action_007",
        description="Review memory usage.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    result = technician.remediate(action)

    assert result.execution_status == "NOT_EXECUTED"
    assert state["executed"] is False

def test_technician_can_execute_registered_remediation_operation():
    from engine.remediation_operation import RemediationOperation

    technician = Technician()

    executed = []

    operation = RemediationOperation(
        operation_id="test_operation",
        description="Review memory-intensive processes.",
        handler=lambda: executed.append(True),
    )

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="test_memory_action",
        description="Review memory-intensive processes.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.remediation_operation_binder.bind(
    action=action,
    operation_id="test_operation",
    )

    bound_action = action

    assert bound_action.operation is operation
    assert action.execution_status == "NOT_EXECUTED"
    assert executed == []

    technician.authorize_remediation(action)

    result = technician.remediate(action)

    assert result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"
    assert operation.execution_status == "EXECUTED"
    assert executed == [True]


def test_technician_cannot_execute_registered_operation_without_authorization():
    from engine.remediation_operation import RemediationOperation

    technician = Technician()

    executed = []

    operation = RemediationOperation(
        operation_id="test_operation",
        description="Review memory-intensive processes.",
        handler=lambda: executed.append(True),
    )

    technician.remediation_operation_registry.register(
        "test_operation",
        operation,
    )

    action = RemediationAction(
        action_id="test_memory_action",
        description="Review memory-intensive processes.",
        category="MEMORY",
        severity="WARNING",
    )

    technician.bind_remediation_operation(action)

    result = technician.remediate(action)

    assert result.execution_status != "EXECUTED"
    assert action.execution_status != "EXECUTED"
    assert operation.execution_status == "NOT_EXECUTED"
    assert executed == []

def test_technician_can_complete_diagnosis_to_remediation_workflow():
    from engine.remediation_operation import RemediationOperation

    technician = Technician()

    result = technician.diagnose()

    actions = result["remediation_actions"]

    assert actions

    action = actions[0]

    assert action.operation is None
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    operation_id = technician.select_remediation_operation(action)

    assert operation_id == "memory_review"

    technician.bind_remediation_operation(action)

    assert action.operation is (
        technician.remediation_operation_registry.get(
            "memory_review"
        )
    )

    assert action.execution_status == "NOT_EXECUTED"
    assert action.operation.execution_status == "NOT_EXECUTED"

    technician.authorize_remediation(action)

    assert action.authorization_status == "AUTHORIZED"

    remediation_result = technician.remediate(action)

    assert remediation_result.execution_status == "EXECUTED"
    assert action.execution_status == "EXECUTED"
    assert action.operation.execution_status == "EXECUTED"

def test_technician_loads_approved_remediation_operations():
    from engine.remediation_operation import RemediationOperation

    technician = Technician()

    operation = technician.remediation_operation_registry.get(
        "memory_review"
    )

    assert isinstance(operation, RemediationOperation)
    assert operation.operation_id == "memory_review"
    assert operation.execution_status == "NOT_EXECUTED"


def test_technician_does_not_auto_bind_catalog_operation():
    technician = Technician()

    result = technician.diagnose()

    actions = result["remediation_actions"]

    assert actions

    for action in actions:
        assert action.operation is None
        assert action.authorization_status == "UNAUTHORIZED"
        assert action.execution_status == "NOT_EXECUTED"
