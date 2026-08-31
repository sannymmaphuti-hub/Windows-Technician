# ==========================================
# Windows Technician v0.3
# MEMORY INTELLIGENCE TESTS
# ==========================================

from engine.intelligence.memory_intelligence import MemoryIntelligence


def test_memory_intelligence_normal_usage():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=50.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 500.0
        }
    )

    assert result["severity"] == "INFO"


def test_memory_intelligence_warning_usage():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=85.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 1500.0
        }
    )

    assert result["severity"] == "WARNING"


def test_memory_intelligence_critical_usage():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=95.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 3000.0
        }
    )

    assert result["severity"] == "CRITICAL"


def test_memory_intelligence_returns_process_identity():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=90.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 2000.0
        }
    )

    assert result["pid"] == 1234
    assert result["name"] == "chrome.exe"


def test_memory_intelligence_returns_memory_usage():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=90.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 2000.0
        }
    )

    assert result["process_memory_mb"] == 2000.0
    assert result["system_memory_percent"] == 90.0


def test_memory_intelligence_identifies_significant_consumer():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=90.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 2000.0
        }
    )

    assert result["is_significant_consumer"] is True


def test_memory_intelligence_normal_consumer():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=50.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 500.0
        }
    )

    assert result["is_significant_consumer"] is False


def test_memory_intelligence_builds_message():

    intelligence = MemoryIntelligence()

    result = intelligence.analyze(
        system_memory_percent=90.0,
        process={
            "pid": 1234,
            "name": "chrome.exe",
            "memory_mb": 2000.0
        }
    )

    assert "chrome.exe" in result["message"]
    assert "2000.00" in result["message"]
