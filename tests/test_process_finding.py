# ==========================================
# Windows Technician v0.5
# PROCESS FINDING TESTS
# ==========================================

from engine.intelligence.process_finding import ProcessFindingBuilder


def test_process_finding_builder_exists():

    builder = ProcessFindingBuilder()

    assert builder is not None


def test_process_finding_from_warning_intelligence():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 85.0,
        "system_cpu_percent": 90.0,
        "severity": "WARNING",
        "behavior": "PERSISTENT",
        "is_significant_contributor": True,
        "message": (
            "chrome.exe is using 85.00% CPU "
            "while system CPU utilization is 90.00%."
        )
    }

    finding = builder.build(intelligence)

    assert finding["category"] == "PROCESS"
    assert finding["severity"] == "WARNING"
    assert finding["pid"] == 1234
    assert finding["process"] == "chrome.exe"


def test_process_finding_contains_behavior():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 85.0,
        "system_cpu_percent": 90.0,
        "severity": "WARNING",
        "behavior": "PERSISTENT",
        "is_significant_contributor": True,
        "message": "High CPU contribution."
    }

    finding = builder.build(intelligence)

    assert finding["behavior"] == "PERSISTENT"


def test_process_finding_contains_contribution():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 85.0,
        "system_cpu_percent": 90.0,
        "severity": "WARNING",
        "behavior": "PERSISTENT",
        "is_significant_contributor": True,
        "message": "High CPU contribution."
    }

    finding = builder.build(intelligence)

    assert finding["is_significant_contributor"] is True


def test_process_finding_contains_message():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 85.0,
        "system_cpu_percent": 90.0,
        "severity": "WARNING",
        "behavior": "SPIKE",
        "is_significant_contributor": True,
        "message": "High CPU contribution."
    }

    finding = builder.build(intelligence)

    assert "message" in finding
    assert isinstance(finding["message"], str)


def test_process_finding_preserves_confidence():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 85.0,
        "system_cpu_percent": 90.0,
        "severity": "WARNING",
        "behavior": "PERSISTENT",
        "is_significant_contributor": True,
        "confidence": 0.92,
        "message": "High CPU contribution."
    }

    finding = builder.build(intelligence)

    assert finding["confidence"] == 0.92


def test_process_finding_normal_behavior():

    builder = ProcessFindingBuilder()

    intelligence = {
        "pid": 1234,
        "name": "chrome.exe",
        "process_cpu_percent": 40.0,
        "system_cpu_percent": 50.0,
        "severity": "INFO",
        "behavior": "NORMAL",
        "is_significant_contributor": False,
        "message": "Normal CPU usage."
    }

    finding = builder.build(intelligence)

    assert finding["category"] == "PROCESS"
    assert finding["severity"] == "INFO"
    assert finding["behavior"] == "NORMAL"


def test_process_finding_rejects_missing_intelligence():

    builder = ProcessFindingBuilder()

    try:
        builder.build(None)
        assert False
    except ValueError:
        assert True

