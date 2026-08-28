# ==========================================
# WINDOWS TECHNICIAN v0.2
# MEMORY DIAGNOSTIC ROOT CAUSE TESTS
# ==========================================

from engine.root_cause_analyzer import RootCauseAnalyzer


def test_memory_diagnostic_root_cause():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "category": "MEMORY DIAGNOSTIC",
            "severity": "CRITICAL",
            "process": "chrome.exe",
            "pid": 1234,
            "process_memory_mb": 7000.0,
            "system_memory_percent": 92.0,
            "behavior": "PERSISTENT",
            "persistence_ratio": 0.80,
            "trend": "RISING",
            "change_percent": 15.0,
            "message": (
                "Critical memory pressure detected."
            )
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    assert len(result) == 1

    candidate = result[0]

    assert candidate["category"] == "MEMORY"

    assert candidate["confidence"] >= 0.80

    assert "Memory pressure" in candidate["cause"]


def test_memory_diagnostic_root_cause_preserves_process():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "category": "MEMORY DIAGNOSTIC",
            "severity": "CRITICAL",
            "process": "chrome.exe",
            "pid": 1234,
            "process_memory_mb": 7000.0,
            "system_memory_percent": 92.0,
            "behavior": "PERSISTENT",
            "persistence_ratio": 0.80,
            "trend": "RISING",
            "change_percent": 15.0,
            "message": (
                "Critical memory pressure detected."
            )
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    candidate = result[0]

    assert candidate["process"] == "chrome.exe"

    assert candidate["pid"] == 1234


def test_memory_diagnostic_root_cause_preserves_evidence():

    analyzer = RootCauseAnalyzer()

    diagnostic_message = (
        "Critical memory pressure detected."
    )

    findings = [

        {
            "category": "MEMORY DIAGNOSTIC",
            "severity": "CRITICAL",
            "process": "chrome.exe",
            "pid": 1234,
            "process_memory_mb": 7000.0,
            "system_memory_percent": 92.0,
            "behavior": "PERSISTENT",
            "persistence_ratio": 0.80,
            "trend": "RISING",
            "change_percent": 15.0,
            "message": diagnostic_message
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    candidate = result[0]

    assert diagnostic_message in candidate["evidence"]