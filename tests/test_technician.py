from application.technician import Technician


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