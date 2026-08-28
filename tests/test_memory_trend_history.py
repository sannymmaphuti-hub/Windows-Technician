# ==========================================
# WINDOWS TECHNICIAN v0.2
# MEMORY TREND HISTORY TESTS
# ==========================================

from engine.analyzer import Analyzer


class FakeMemoryCollector:

    category = "MEMORY"

    def __init__(self, usage_percent):
        self.usage_percent = usage_percent

    def collect(self):
        return {
            "usage_percent": self.usage_percent
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
                }
            ]
        }


def create_analyzer(memory_usage):

    return Analyzer(
        collectors=[
            FakeMemoryCollector(memory_usage),
            FakeProcessCollector()
        ]
    )


def test_memory_history_starts_empty():

    analyzer = create_analyzer(60.0)

    assert analyzer.memory_history == []


def test_first_memory_observation_is_recorded():

    analyzer = create_analyzer(60.0)

    analyzer.analyze()

    assert analyzer.memory_history == [60.0]


def test_memory_history_accumulates_observations():

    analyzer = Analyzer(
        collectors=[
            FakeProcessCollector()
        ]
    )

    memory_collector = FakeMemoryCollector(60.0)

    analyzer.collectors.insert(
        0,
        memory_collector
    )

    analyzer.analyze()

    memory_collector.usage_percent = 70.0
    analyzer.analyze()

    memory_collector.usage_percent = 80.0
    analyzer.analyze()

    assert analyzer.memory_history == [
        60.0,
        70.0,
        80.0
    ]


def test_memory_history_detects_rising_trend():

    analyzer = Analyzer(
        collectors=[
            FakeProcessCollector()
        ]
    )

    memory_collector = FakeMemoryCollector(60.0)

    analyzer.collectors.insert(
        0,
        memory_collector
    )

    analyzer.analyze()

    memory_collector.usage_percent = 70.0
    analyzer.analyze()

    memory_collector.usage_percent = 80.0
    result = analyzer.analyze()

    trend = result["memory_trend_intelligence"]

    assert trend["trend"] == "RISING"


def test_memory_history_detects_falling_trend():

    analyzer = Analyzer(
        collectors=[
            FakeProcessCollector()
        ]
    )

    memory_collector = FakeMemoryCollector(90.0)

    analyzer.collectors.insert(
        0,
        memory_collector
    )

    analyzer.analyze()

    memory_collector.usage_percent = 80.0
    analyzer.analyze()

    memory_collector.usage_percent = 70.0
    result = analyzer.analyze()

    trend = result["memory_trend_intelligence"]

    assert trend["trend"] == "FALLING"


def test_memory_history_does_not_reset():

    analyzer = Analyzer(
        collectors=[
            FakeProcessCollector()
        ]
    )

    memory_collector = FakeMemoryCollector(50.0)

    analyzer.collectors.insert(
        0,
        memory_collector
    )

    analyzer.analyze()

    memory_collector.usage_percent = 60.0
    analyzer.analyze()

    memory_collector.usage_percent = 70.0
    analyzer.analyze()

    assert len(analyzer.memory_history) == 3