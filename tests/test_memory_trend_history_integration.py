# ==========================================
# Windows Technician v0.3
# MEMORY TREND HISTORY INTEGRATION TESTS
# ==========================================

from engine.analyzer import Analyzer


class FakeMemoryCollector:

    category = "MEMORY"

    def collect(self):
        return {
            "usage_percent": 92.0
        }


class FakeProcessCollector:

    category = "PROCESS"

    def collect(self):
        return {
            "processes": [
                {
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 20.0,
                    "memory_mb": 7000.0
                },
                {
                    "pid": 5678,
                    "name": "code.exe",
                    "cpu_percent": 10.0,
                    "memory_mb": 1000.0
                }
            ]
        }


def test_analyzer_contains_memory_history():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_history" in result


def test_analyzer_records_memory_observation():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    analyzer.analyze()

    assert len(analyzer.memory_history) == 1
    assert analyzer.memory_history[0] == 92.0


def test_analyzer_accumulates_memory_history():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    analyzer.analyze()
    analyzer.analyze()
    analyzer.analyze()

    assert len(analyzer.memory_history) == 3


def test_analyzer_memory_history_does_not_reset():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    analyzer.analyze()

    first_history = analyzer.memory_history.copy()

    analyzer.analyze()

    assert len(analyzer.memory_history) == 2
    assert analyzer.memory_history[:1] == first_history


def test_memory_history_feeds_trend_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_trend_intelligence" in result
