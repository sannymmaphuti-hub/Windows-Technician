# ==========================================
# Windows Technician v0.6
# MEMORY DIAGNOSTIC FINDING TESTS
# ==========================================

from engine.intelligence.memory_diagnostic_finding import (
    MemoryDiagnosticFindingBuilder
)


def test_memory_diagnostic_finding_builds():

    builder = MemoryDiagnosticFindingBuilder()

    intelligence = {
        "severity": "CRITICAL",
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0,
        "system_memory_percent": 92.0,
        "behavior": "PERSISTENT",
        "persistence_ratio": 0.80,
        "trend": "RISING",
        "change_percent": 25.0,
        "is_significant_rise": True,
        "message": "Critical memory pressure detected."
    }

    finding = builder.build(intelligence)

    assert finding["category"] == "MEMORY"
    assert finding["severity"] == "CRITICAL"
    assert finding["process"] == "chrome.exe"
    assert finding["pid"] == 1234


def test_memory_diagnostic_finding_preserves_memory_usage():

    builder = MemoryDiagnosticFindingBuilder()

    intelligence = {
        "severity": "WARNING",
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0,
        "system_memory_percent": 92.0,
        "behavior": "PERSISTENT",
        "persistence_ratio": 0.80,
        "trend": "RISING",
        "change_percent": 15.0,
        "is_significant_rise": False,
        "message": "Elevated memory pressure detected."
    }

    finding = builder.build(intelligence)

    assert finding["process_memory_mb"] == 7000.0
    assert finding["system_memory_percent"] == 92.0


def test_memory_diagnostic_finding_preserves_trend():

    builder = MemoryDiagnosticFindingBuilder()

    intelligence = {
        "severity": "WARNING",
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0,
        "system_memory_percent": 92.0,
        "behavior": "PERSISTENT",
        "persistence_ratio": 0.80,
        "trend": "RISING",
        "change_percent": 15.0,
        "is_significant_rise": False,
        "message": "Elevated memory pressure detected."
    }

    finding = builder.build(intelligence)

    assert finding["trend"] == "RISING"
    assert finding["change_percent"] == 15.0


def test_memory_diagnostic_finding_preserves_behavior():

    builder = MemoryDiagnosticFindingBuilder()

    intelligence = {
        "severity": "WARNING",
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0,
        "system_memory_percent": 92.0,
        "behavior": "PERSISTENT",
        "persistence_ratio": 0.80,
        "trend": "RISING",
        "change_percent": 15.0,
        "is_significant_rise": False,
        "message": "Elevated memory pressure detected."
    }

    finding = builder.build(intelligence)

    assert finding["behavior"] == "PERSISTENT"
    assert finding["persistence_ratio"] == 0.80


def test_memory_diagnostic_finding_preserves_message():

    builder = MemoryDiagnosticFindingBuilder()

    intelligence = {
        "severity": "CRITICAL",
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0,
        "system_memory_percent": 92.0,
        "behavior": "PERSISTENT",
        "persistence_ratio": 0.80,
        "trend": "RISING",
        "change_percent": 25.0,
        "is_significant_rise": True,
        "message": "Critical memory pressure detected."
    }

    finding = builder.build(intelligence)

    assert finding["message"] == (
        "Critical memory pressure detected."
    )


def test_memory_diagnostic_finding_handles_missing_intelligence():

    builder = MemoryDiagnosticFindingBuilder()

    try:
        builder.build(None)
        assert False
    except ValueError:
        assert True
