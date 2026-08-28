# ==========================================
# WINDOWS TECHNICIAN v0.2
# MEMORY TREND INTELLIGENCE INTEGRATION TESTS
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


def test_analyzer_runs_memory_trend_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_trend_intelligence" in result


def test_memory_trend_intelligence_identifies_trend():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    trend = result["memory_trend_intelligence"]

    assert trend["trend"] in (
        "RISING",
        "FALLING",
        "STABLE",
        "UNKNOWN"
    )


def test_memory_trend_intelligence_reports_change():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    trend = result["memory_trend_intelligence"]

    assert "change_percent" in trend


def test_memory_trend_intelligence_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert "findings" in diagnosis