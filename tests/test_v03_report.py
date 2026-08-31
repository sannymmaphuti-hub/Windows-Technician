# ==========================================
# WINDOWS TECHNICIAN v0.3
# REPORT BOUNDARY TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.report import generate_case_report


def create_test_case():

    case = DiagnosticCase()

    case.set_evidence({
        "system": {
            "computer_name": "V03-TEST-PC"
        }
    })

    case.set_findings([
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "High CPU usage detected."
        }
    ])

    case.set_correlations([
        {
            "relationship": "CPU + PROCESS",
            "message": "A process is contributing to CPU pressure."
        }
    ])

    case.set_root_causes([
        {
            "cause": "High CPU process",
            "confidence": 0.90
        }
    ])

    case.set_recommendations([
        {
            "category": "CPU",
            "recommendation": "Investigate the high CPU process."
        }
    ])

    case.set_process_intelligence({
        "name": "test.exe",
        "behavior": "HIGH_CPU",
        "severity": "WARNING"
    })

    case.set_memory_intelligence({
        "process": "test.exe",
        "severity": "NORMAL"
    })

    case.set_memory_history([
        50.0,
        55.0,
        60.0
    ])

    case.set_memory_trend_intelligence({
        "trend": "RISING",
        "severity": "WARNING"
    })

    case.set_memory_temporal_intelligence({
        "behavior": "PERSISTENT",
        "severity": "WARNING"
    })

    case.set_memory_diagnostic_intelligence({
        "diagnosis": "POSSIBLE_MEMORY_PRESSURE",
        "severity": "WARNING"
    })

    case.set_root_cause_candidates([
        {
            "cause": "High CPU process",
            "confidence": 0.90
        }
    ])

    case.set_primary_root_cause({
        "cause": "High CPU process",
        "confidence": 0.90
    })

    case.set_status("WARNING")

    return case


def test_case_report_can_be_generated():

    case = create_test_case()

    report = generate_case_report(case)

    assert isinstance(report, str)
    assert len(report) > 0


def test_case_report_contains_v03_status():

    case = create_test_case()

    report = generate_case_report(case)

    assert "WARNING" in report


def test_case_report_contains_case_findings():

    case = create_test_case()

    report = generate_case_report(case)

    assert "High CPU usage detected." in report


def test_case_report_contains_root_cause():

    case = create_test_case()

    report = generate_case_report(case)

    assert "High CPU process" in report


def test_case_report_contains_recommendations():

    case = create_test_case()

    report = generate_case_report(case)

    assert "Investigate the high CPU process." in report


def test_case_report_contains_intelligence():

    case = create_test_case()

    report = generate_case_report(case)

    assert "HIGH_CPU" in report
    assert "RISING" in report
    assert "PERSISTENT" in report
    assert "POSSIBLE_MEMORY_PRESSURE" in report


def test_case_report_does_not_mutate_case():

    case = create_test_case()

    before = case.__dict__.copy()

    generate_case_report(case)

    after = case.__dict__.copy()

    assert after == before
