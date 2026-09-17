# ==========================================
# Windows Technician v0.5
# CPU ROOT CAUSE TESTS
# ==========================================

from engine.root_cause_analyzer import RootCauseAnalyzer


def test_cpu_root_cause():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "category": "CPU",
            "severity": "CRITICAL",
            "cpu_usage_percent": 94.0,
            "process": "chrome.exe",
            "pid": 1234,
            "process_cpu_percent": 87.0,
            "message": (
                "Critical CPU pressure detected."
            )
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    assert len(result) == 1

    candidate = result[0]

    assert candidate["category"] == "CPU"

    assert candidate["confidence"] >= 0.80

    assert "CPU pressure" in candidate["cause"]


def test_cpu_root_cause_preserves_process():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "category": "CPU",
            "severity": "CRITICAL",
            "cpu_usage_percent": 94.0,
            "process": "chrome.exe",
            "pid": 1234,
            "process_cpu_percent": 87.0,
            "message": (
                "Critical CPU pressure detected."
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


def test_cpu_root_cause_preserves_evidence():

    analyzer = RootCauseAnalyzer()

    diagnostic_message = (
        "Critical CPU pressure detected."
    )

    findings = [

        {
            "category": "CPU",
            "severity": "CRITICAL",
            "cpu_usage_percent": 94.0,
            "process": "chrome.exe",
            "pid": 1234,
            "process_cpu_percent": 87.0,
            "message": diagnostic_message
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    candidate = result[0]

    assert diagnostic_message in (
        candidate["evidence"]
    )


def test_cpu_root_cause_requires_high_severity():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "category": "CPU",
            "severity": "INFO",
            "cpu_usage_percent": 45.0,
            "process": "chrome.exe",
            "pid": 1234,
            "process_cpu_percent": 10.0,
            "message": (
                "Normal CPU activity."
            )
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=[]
    )

    assert len(result) == 0

