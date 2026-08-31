# ==========================================
# Windows Technician v0.3
# MEMORY TEMPORAL INTELLIGENCE INTEGRATION TESTS
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
                    "memory_mb": 7000.0,
                    "status": "running"
                },
                {
                    "pid": 5678,
                    "name": "code.exe",
                    "cpu_percent": 10.0,
                    "memory_mb": 1000.0,
                    "status": "running"
                }
            ]
        }


def test_analyzer_runs_memory_temporal_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_temporal_intelligence" in result


def test_memory_temporal_intelligence_identifies_behavior():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    temporal = result["memory_temporal_intelligence"]

    assert temporal["behavior"] in [
        "NORMAL",
        "SPIKE",
        "PERSISTENT"
    ]


def test_memory_temporal_intelligence_reports_persistence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    temporal = result["memory_temporal_intelligence"]

    assert "persistence_ratio" in temporal


def test_memory_temporal_intelligence_identifies_process():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    temporal = result["memory_temporal_intelligence"]

    assert temporal["name"] == "chrome.exe"
    assert temporal["pid"] == 1234


def test_memory_temporal_intelligence_enters_finding():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_temporal_finding" in result


def test_memory_temporal_finding_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis["total_findings"] >= 1
