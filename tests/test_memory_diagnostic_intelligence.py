# ==========================================
# Windows Technician v0.3
# MEMORY DIAGNOSTIC INTELLIGENCE TESTS
# ==========================================


from engine.intelligence.memory_diagnostic_intelligence import (
    MemoryDiagnosticIntelligence
)


def test_memory_diagnostic_identifies_critical_rising_memory():

    intelligence = MemoryDiagnosticIntelligence()

    temporal = {
        "behavior": "PERSISTENT",
        "is_sustained_consumer": True,
        "persistence_ratio": 0.8,
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0
    }

    trend = {
        "trend": "RISING",
        "change_percent": 35.0,
        "is_significant_rise": True
    }

    result = intelligence.analyze(
        system_memory_percent=92.0,
        temporal_intelligence=temporal,
        trend_intelligence=trend
    )

    assert result["severity"] == "CRITICAL"


def test_memory_diagnostic_identifies_warning_rising_memory():

    intelligence = MemoryDiagnosticIntelligence()

    temporal = {
        "behavior": "PERSISTENT",
        "is_sustained_consumer": True,
        "persistence_ratio": 0.7,
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 5000.0
    }

    trend = {
        "trend": "RISING",
        "change_percent": 20.0,
        "is_significant_rise": True
    }

    result = intelligence.analyze(
        system_memory_percent=85.0,
        temporal_intelligence=temporal,
        trend_intelligence=trend
    )

    assert result["severity"] == "WARNING"


def test_memory_diagnostic_identifies_normal_stable_memory():

    intelligence = MemoryDiagnosticIntelligence()

    temporal = {
        "behavior": "NORMAL",
        "is_sustained_consumer": False,
        "persistence_ratio": 0.2,
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 2500.0
    }

    trend = {
        "trend": "STABLE",
        "change_percent": 2.0,
        "is_significant_rise": False
    }

    result = intelligence.analyze(
        system_memory_percent=50.0,
        temporal_intelligence=temporal,
        trend_intelligence=trend
    )

    assert result["severity"] == "INFO"


def test_memory_diagnostic_preserves_process_identity():

    intelligence = MemoryDiagnosticIntelligence()

    temporal = {
        "behavior": "PERSISTENT",
        "is_sustained_consumer": True,
        "persistence_ratio": 0.8,
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0
    }

    trend = {
        "trend": "RISING",
        "change_percent": 35.0,
        "is_significant_rise": True
    }

    result = intelligence.analyze(
        system_memory_percent=92.0,
        temporal_intelligence=temporal,
        trend_intelligence=trend
    )

    assert result["name"] == "chrome.exe"
    assert result["pid"] == 1234


def test_memory_diagnostic_reports_reason():

    intelligence = MemoryDiagnosticIntelligence()

    temporal = {
        "behavior": "PERSISTENT",
        "is_sustained_consumer": True,
        "persistence_ratio": 0.8,
        "name": "chrome.exe",
        "pid": 1234,
        "process_memory_mb": 7000.0
    }

    trend = {
        "trend": "RISING",
        "change_percent": 35.0,
        "is_significant_rise": True
    }

    result = intelligence.analyze(
        system_memory_percent=92.0,
        temporal_intelligence=temporal,
        trend_intelligence=trend
    )

    assert "message" in result
    assert result["message"]


def test_memory_diagnostic_handles_missing_temporal_intelligence():

    intelligence = MemoryDiagnosticIntelligence()

    trend = {
        "trend": "RISING",
        "change_percent": 20.0,
        "is_significant_rise": True
    }

    result = intelligence.analyze(
        system_memory_percent=85.0,
        temporal_intelligence=None,
        trend_intelligence=trend
    )

    assert result is None
