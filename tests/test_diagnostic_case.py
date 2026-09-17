# ==========================================
# Windows Technician v0.5
# DIAGNOSTIC CASE TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase


def test_diagnostic_case_can_be_created():

    case = DiagnosticCase()

    assert case is not None


def test_diagnostic_case_starts_empty():

    case = DiagnosticCase()

    assert case.evidence == {}
    assert case.findings == []
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []


def test_diagnostic_case_starts_with_normal_status():

    case = DiagnosticCase()

    assert case.status == "NORMAL"


def test_diagnostic_case_can_store_evidence():

    case = DiagnosticCase()

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    case.set_evidence(evidence)

    assert case.evidence == evidence


def test_diagnostic_case_can_store_findings():

    case = DiagnosticCase()

    findings = [
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "High CPU usage."
        }
    ]

    case.set_findings(findings)

    assert case.findings == findings


def test_diagnostic_case_can_store_correlations():

    case = DiagnosticCase()

    correlations = [
        {
            "relationship": "CPU + MEMORY"
        }
    ]

    case.set_correlations(correlations)

    assert case.correlations == correlations


def test_diagnostic_case_can_store_root_causes():

    case = DiagnosticCase()

    root_causes = [
        {
            "cause": "Process consuming excessive resources.",
            "confidence": 0.85
        }
    ]

    case.set_root_causes(root_causes)

    assert case.root_causes == root_causes


def test_diagnostic_case_can_store_recommendations():

    case = DiagnosticCase()

    recommendations = [
        {
            "category": "CPU",
            "recommendation": "Investigate high CPU process."
        }
    ]

    case.set_recommendations(recommendations)

    assert case.recommendations == recommendations


def test_diagnostic_case_can_store_process_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "name": "chrome.exe",
        "behavior": "HIGH_CPU",
        "severity": "WARNING"
    }

    case.set_process_intelligence(intelligence)

    assert case.process_intelligence == intelligence


def test_diagnostic_case_can_store_memory_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "process": "chrome.exe",
        "severity": "WARNING"
    }

    case.set_memory_intelligence(intelligence)

    assert case.memory_intelligence == intelligence


def test_diagnostic_case_can_store_memory_history():

    case = DiagnosticCase()

    history = [
        61.2,
        68.4,
        74.8,
        81.3
    ]

    case.set_memory_history(history)

    assert case.memory_history == history


def test_diagnostic_case_can_store_memory_trend_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "trend": "RISING",
        "severity": "WARNING"
    }

    case.set_memory_trend_intelligence(intelligence)

    assert case.memory_trend_intelligence == intelligence


def test_diagnostic_case_can_store_memory_temporal_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "behavior": "PERSISTENT",
        "severity": "WARNING"
    }

    case.set_memory_temporal_intelligence(intelligence)

    assert case.memory_temporal_intelligence == intelligence


def test_diagnostic_case_can_store_memory_diagnostic_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "diagnosis": "POSSIBLE_MEMORY_PRESSURE",
        "severity": "WARNING"
    }

    case.set_memory_diagnostic_intelligence(intelligence)

    assert case.memory_diagnostic_intelligence == intelligence


def test_diagnostic_case_can_store_root_cause_candidates():

    case = DiagnosticCase()

    candidates = [
        {
            "cause": "High memory consuming process",
            "confidence": 0.85
        }
    ]

    case.set_root_cause_candidates(candidates)

    assert case.root_cause_candidates == candidates


def test_diagnostic_case_can_store_primary_root_cause():

    case = DiagnosticCase()

    primary = {
        "cause": "High memory consuming process",
        "confidence": 0.85
    }

    case.set_primary_root_cause(primary)

    assert case.primary_root_cause == primary

def test_diagnostic_case_can_store_status():

    case = DiagnosticCase()

    case.set_status("WARNING")

    assert case.status == "WARNING"


def test_diagnostic_case_can_store_critical_status():

    case = DiagnosticCase()

    case.set_status("CRITICAL")

    assert case.status == "CRITICAL"


def test_diagnostic_case_status_defaults_to_normal():

    case = DiagnosticCase()

    assert case.status == "NORMAL"

