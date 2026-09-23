# ==========================================
# Windows Technician v0.6
# MEMORY TREND INTELLIGENCE TESTS
# ==========================================

from engine.intelligence.memory_trend_intelligence import (
    MemoryTrendIntelligence
)


def test_memory_trend_detects_rising_memory():

    intelligence = MemoryTrendIntelligence()

    history = [
        40.0,
        48.0,
        57.0,
        66.0,
        75.0
    ]

    result = intelligence.analyze(
        memory_history=history
    )

    assert result["trend"] == "RISING"


def test_memory_trend_detects_falling_memory():

    intelligence = MemoryTrendIntelligence()

    history = [
        85.0,
        76.0,
        68.0,
        59.0,
        50.0
    ]

    result = intelligence.analyze(
        memory_history=history
    )

    assert result["trend"] == "FALLING"


def test_memory_trend_detects_stable_memory():

    intelligence = MemoryTrendIntelligence()

    history = [
        50.0,
        51.0,
        49.0,
        50.0,
        51.0
    ]

    result = intelligence.analyze(
        memory_history=history
    )

    assert result["trend"] == "STABLE"


def test_memory_trend_reports_change():

    intelligence = MemoryTrendIntelligence()

    history = [
        40.0,
        50.0,
        60.0,
        70.0,
        80.0
    ]

    result = intelligence.analyze(
        memory_history=history
    )

    assert "change_percent" in result
    assert result["change_percent"] == 40.0


def test_memory_trend_detects_significant_rise():

    intelligence = MemoryTrendIntelligence()

    history = [
        40.0,
        50.0,
        60.0,
        70.0,
        80.0
    ]

    result = intelligence.analyze(
        memory_history=history
    )

    assert result["is_significant_trend"] is True


def test_memory_trend_handles_empty_history():

    intelligence = MemoryTrendIntelligence()

    result = intelligence.analyze(
        memory_history=[]
    )

    assert result["trend"] == "UNKNOWN"
    assert result["change_percent"] == 0.0
    assert result["is_significant_trend"] is False
