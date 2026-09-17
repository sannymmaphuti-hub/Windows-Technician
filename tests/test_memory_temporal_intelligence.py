# ==========================================
# Windows Technician v0.5
# MEMORY TEMPORAL INTELLIGENCE TESTS
# ==========================================

from engine.intelligence.memory_temporal_intelligence import (
    MemoryTemporalIntelligence
)


def test_memory_temporal_intelligence_detects_sustained_memory():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 7000.0
    }

    history = [
        6500.0,
        6800.0,
        7000.0,
        7200.0,
        7100.0
    ]

    result = intelligence.analyze(
        system_memory_percent=92.0,
        process=process,
        memory_history=history
    )

    assert result["behavior"] == "PERSISTENT"


def test_memory_temporal_intelligence_detects_memory_spike():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 8000.0
    }

    history = [
        2000.0,
        2200.0,
        2100.0,
        2300.0,
        8000.0
    ]

    result = intelligence.analyze(
        system_memory_percent=92.0,
        process=process,
        memory_history=history
    )

    assert result["behavior"] == "SPIKE"


def test_memory_temporal_intelligence_detects_normal_history():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 2500.0
    }

    history = [
        2400.0,
        2500.0,
        2450.0,
        2550.0,
        2500.0
    ]

    result = intelligence.analyze(
        system_memory_percent=50.0,
        process=process,
        memory_history=history
    )

    assert result["behavior"] == "NORMAL"


def test_memory_temporal_intelligence_reports_persistence_ratio():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 7000.0
    }

    history = [
        7000.0,
        7200.0,
        6800.0,
        3000.0,
        2500.0
    ]

    result = intelligence.analyze(
        system_memory_percent=92.0,
        process=process,
        memory_history=history
    )

    assert "persistence_ratio" in result
    assert 0.0 <= result["persistence_ratio"] <= 1.0


def test_memory_temporal_intelligence_identifies_sustained_consumer():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 7000.0
    }

    history = [
        6500.0,
        6800.0,
        7000.0,
        7200.0,
        7100.0
    ]

    result = intelligence.analyze(
        system_memory_percent=92.0,
        process=process,
        memory_history=history
    )

    assert result["is_sustained_consumer"] is True


def test_memory_temporal_intelligence_handles_empty_history():

    intelligence = MemoryTemporalIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "memory_mb": 7000.0
    }

    result = intelligence.analyze(
        system_memory_percent=92.0,
        process=process,
        memory_history=[]
    )

    assert result["behavior"] == "UNKNOWN"

