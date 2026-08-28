# ==========================================
# WINDOWS TECHNICIAN v0.2
# PROCESS INTELLIGENCE TESTS
# ==========================================

from engine.intelligence.process_intelligence import (
    ProcessIntelligence
)


def test_process_intelligence_normal_cpu():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 20.0
    }

    result = intelligence.analyze(
        system_cpu_percent=40.0,
        process=process
    )

    assert result["severity"] == "INFO"

    assert result[
        "is_significant_contributor"
    ] is False


def test_process_intelligence_warning_cpu():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 85.0
    }

    result = intelligence.analyze(
        system_cpu_percent=85.0,
        process=process
    )

    assert result["severity"] == "WARNING"

    assert result[
        "is_significant_contributor"
    ] is True


def test_process_intelligence_critical_cpu():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 90.0
    }

    result = intelligence.analyze(
        system_cpu_percent=97.0,
        process=process
    )

    assert result["severity"] == "CRITICAL"


def test_process_intelligence_detects_persistent_cpu():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 90.0
    }

    history = [
        85.0,
        88.0,
        91.0,
        86.0,
        90.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=95.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "PERSISTENT"


def test_process_intelligence_detects_cpu_spike():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 90.0
    }

    history = [
        10.0,
        12.0,
        91.0,
        8.0,
        10.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=90.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "SPIKE"


def test_process_intelligence_detects_normal_behavior():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 20.0
    }

    history = [
        10.0,
        15.0,
        20.0,
        18.0,
        12.0
    ]

    result = intelligence.analyze(
        system_cpu_percent=40.0,
        process=process,
        cpu_history=history
    )

    assert result["behavior"] == "NORMAL"


def test_process_intelligence_handles_missing_history():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 100,
        "name": "chrome.exe",
        "cpu_percent": 20.0
    }

    result = intelligence.analyze(
        system_cpu_percent=40.0,
        process=process
    )

    assert result["behavior"] == "UNKNOWN"


def test_process_intelligence_returns_process_identity():

    intelligence = ProcessIntelligence()

    process = {
        "pid": 1234,
        "name": "python.exe",
        "cpu_percent": 50.0
    }

    result = intelligence.analyze(
        system_cpu_percent=50.0,
        process=process
    )

    assert result["pid"] == 1234
    assert result["name"] == "python.exe"