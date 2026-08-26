# ==========================================
# WINDOWS TECHNICIAN v0.1
# APPLICATION TEST
# ==========================================

from application.app import TechnicianApp


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