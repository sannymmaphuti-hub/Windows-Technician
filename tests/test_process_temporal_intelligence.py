# ==========================================
# Windows Technician v0.6
# TEMPORAL PROCESS INTELLIGENCE TESTS
# ==========================================

from engine.intelligence.process_intelligence import ProcessIntelligence


def test_temporal_intelligence_detects_sustained_cpu():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 85.0
    }

    history = [
        82.0,
        85.0,
        88.0,
        91.0,
        87.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=92.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "PERSISTENT"


def test_temporal_intelligence_detects_cpu_spike():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 90.0
    }

    history = [
        20.0,
        25.0,
        95.0,
        30.0,
        22.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=90.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "SPIKE"


def test_temporal_intelligence_detects_normal_history():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 20.0
    }

    history = [
        15.0,
        20.0,
        18.0,
        22.0,
        19.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=40.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "NORMAL"


def test_temporal_intelligence_reports_persistence_ratio():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 85.0
    }

    history = [
        80.0,
        85.0,
        90.0,
        40.0,
        30.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=90.0,
        process=process,
        cpu_history=history
    )

    assert "persistence_ratio" in result
    assert result["persistence_ratio"] == 60.0


def test_temporal_intelligence_identifies_sustained_contributor():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 85.0
    }

    history = [
        85.0,
        90.0,
        88.0,
        92.0,
        87.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=95.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "PERSISTENT"
    assert result["is_significant_contributor"] is True


def test_temporal_intelligence_handles_empty_history():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "chrome.exe",
        "cpu_percent": 85.0
    }

    result = intelligence.analyze(
        system_cpu_percent=90.0,
        process=process,
        cpu_history=[]
    )

    assert result["behavior"] == "UNKNOWN"
