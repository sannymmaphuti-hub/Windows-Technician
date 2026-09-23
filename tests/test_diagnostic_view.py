# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC VIEW TESTS
# ==========================================

from application.diagnostic_view import DiagnosticView


def make_diagnostic_result():
    return {
        "evidence": {
            "CPU": {"usage_percent": 25.0}
        },
        "intelligence": {
            "example": "intelligence data"
        },
        "process_intelligence": {
            "name": "example.exe",
            "severity": "INFO"
        },
        "memory_intelligence": {
            "process": "example.exe",
            "severity": "WARNING"
        },
        "memory_history": [70.0, 75.0, 80.0],
        "memory_trend_intelligence": {
            "trend": "INCREASING"
        },
        "memory_temporal_intelligence": {
            "behavior": "SUSTAINED"
        },
        "memory_diagnostic_intelligence": {
            "severity": "WARNING"
        },
        "diagnosis": {
            "evidence": {
                "CPU": {"usage_percent": 25.0}
            },
            "status": "WARNING",
            "total_findings": 2,
            "findings": [
                {
                    "category": "MEMORY",
                    "severity": "WARNING",
                    "issue": "High memory usage"
                },
                {
                    "category": "CPU",
                    "severity": "INFO",
                    "issue": "Normal CPU usage"
                }
            ],
            "correlations": [
                {
                    "type": "MEMORY_PROCESS",
                    "severity": "WARNING"
                }
            ],
            "root_causes": [
                {
                    "cause": "Memory pressure",
                    "confidence": 0.85
                }
            ],
            "recommendations": [
                {
                    "action": "Close unnecessary applications",
                    "priority": "HIGH"
                }
            ]
        },
        "diagnostic_case": {
            "evidence": {
                "CPU": {"usage_percent": 25.0}
            },
            "findings": [
                {
                    "category": "MEMORY",
                    "severity": "WARNING"
                }
            ],
            "correlations": [
                {
                    "type": "MEMORY_PROCESS"
                }
            ],
            "root_causes": [
                {
                    "cause": "Memory pressure"
                }
            ],
            "root_cause_candidates": [
                {
                    "cause": "Memory pressure",
                    "confidence": 0.85
                }
            ],
            "primary_root_cause": {
                "cause": "Memory pressure",
                "confidence": 0.85
            },
            "recommendations": [
                {
                    "action": "Close unnecessary applications"
                }
            ],
            "status": "WARNING",
            "process_intelligence": {
                "name": "example.exe",
                "severity": "INFO"
            },
            "memory_intelligence": {
                "process": "example.exe",
                "severity": "WARNING"
            },
            "memory_history": [70.0, 75.0, 80.0],
            "memory_trend_intelligence": {
                "trend": "INCREASING"
            },
            "memory_temporal_intelligence": {
                "behavior": "SUSTAINED"
            },
            "memory_diagnostic_intelligence": {
                "severity": "WARNING"
            }
        },
        "case_decision": {
            "decision": "INVESTIGATE",
            "confidence": 0.85
        }
    }


def test_diagnostic_view_exposes_diagnosis_summary():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.status == "WARNING"
    assert view.total_findings == 2


def test_diagnostic_view_exposes_findings():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.findings == result["diagnosis"]["findings"]


def test_diagnostic_view_exposes_correlations():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.correlations == result["diagnosis"]["correlations"]


def test_diagnostic_view_exposes_root_cause_information():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.root_causes == result["diagnosis"]["root_causes"]
    assert view.root_cause_candidates == (
        result["diagnostic_case"]["root_cause_candidates"]
    )
    assert view.primary_root_cause == (
        result["diagnostic_case"]["primary_root_cause"]
    )


def test_diagnostic_view_exposes_recommendations():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.recommendations == (
        result["diagnosis"]["recommendations"]
    )


def test_diagnostic_view_exposes_case_decision():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.case_decision == result["case_decision"]


def test_diagnostic_view_exposes_process_and_memory_intelligence():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.process_intelligence == (
        result["diagnostic_case"]["process_intelligence"]
    )

    assert view.memory_intelligence == (
        result["diagnostic_case"]["memory_intelligence"]
    )


def test_diagnostic_view_exposes_memory_analysis():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.memory_history == (
        result["diagnostic_case"]["memory_history"]
    )

    assert view.memory_trend_intelligence == (
        result["diagnostic_case"]["memory_trend_intelligence"]
    )

    assert view.memory_temporal_intelligence == (
        result["diagnostic_case"]["memory_temporal_intelligence"]
    )

    assert view.memory_diagnostic_intelligence == (
        result["diagnostic_case"]["memory_diagnostic_intelligence"]
    )


def test_diagnostic_view_does_not_mutate_original_result():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    view.findings.append({
        "category": "TEST",
        "severity": "INFO"
    })

    assert len(result["diagnosis"]["findings"]) == 2

def test_diagnostic_view_handles_empty_diagnostic_case():
    result = {
        "diagnosis": {
            "status": "HEALTHY",
            "total_findings": 0,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": []
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
            "process_intelligence": None,
            "memory_intelligence": None,
            "memory_history": [],
            "memory_trend_intelligence": None,
            "memory_temporal_intelligence": None,
            "memory_diagnostic_intelligence": None
        },
        "case_decision": {}
    }

    view = DiagnosticView(result)

    assert view.status == "HEALTHY"
    assert view.total_findings == 0
    assert view.findings == []
    assert view.correlations == []
    assert view.root_causes == []
    assert view.root_cause_candidates == []
    assert view.primary_root_cause is None
    assert view.recommendations == []
    assert view.case_decision == {}


def test_diagnostic_view_handles_missing_optional_sections():
    result = {
        "diagnosis": {
            "status": "HEALTHY",
            "total_findings": 0
        },
        "diagnostic_case": {}
    }

    view = DiagnosticView(result)

    assert view.status == "HEALTHY"
    assert view.total_findings == 0
    assert view.findings == []
    assert view.correlations == []
    assert view.root_causes == []
    assert view.root_cause_candidates == []
    assert view.primary_root_cause is None
    assert view.recommendations == []
    assert view.case_decision == {}
    assert view.memory_history == []

def test_diagnostic_view_exposes_evidence():
    result = make_diagnostic_result()

    view = DiagnosticView(result)

    assert view.evidence == result["evidence"]

def test_diagnostic_view_exposes_network_diagnostic_result():
    result = make_diagnostic_result()

    result["network_diagnostic_case"] = {
        "observations": [],
        "signals": [],
        "findings": [],
        "correlations": [],
        "candidates": [],
        "evaluations": [],
        "primary_cause": None,
        "confidences": [],
        "explanations": [],
        "recommendations": [],
    }

    result["network_case_explanation"] = (
        "network explanation"
    )

    view = DiagnosticView(result)

    assert view.network_diagnostic_case == (
        result["network_diagnostic_case"]
    )

    assert view.network_case_explanation == (
        result["network_case_explanation"]
    )

def test_diagnostic_view_isolates_network_diagnostic_result():
    result = make_diagnostic_result()

    result["network_diagnostic_case"] = {
        "observations": ["observation"],
        "signals": ["signal"],
        "findings": ["finding"],
        "correlations": [],
        "candidates": [],
        "evaluations": [],
        "primary_cause": None,
        "confidences": [],
        "explanations": [],
        "recommendations": [],
    }

    result["network_case_explanation"] = {
        "summary": "Network explanation"
    }

    view = DiagnosticView(result)

    view.network_diagnostic_case[
        "observations"
    ].append("changed")

    view.network_case_explanation[
        "summary"
    ] = "changed"

    assert result[
        "network_diagnostic_case"
    ]["observations"] == ["observation"]

    assert result[
        "network_case_explanation"
    ]["summary"] == "Network explanation"

