# ==========================================
# Windows Technician v0.5
# MEMORY INTELLIGENCE INTEGRATION TESTS
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


def test_analyzer_runs_memory_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_intelligence" in result


def test_memory_intelligence_identifies_top_consumer():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    intelligence = result["memory_intelligence"]

    assert intelligence["name"] == "chrome.exe"
    assert intelligence["pid"] == 1234


def test_memory_intelligence_detects_critical_pressure():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    intelligence = result["memory_intelligence"]

    assert intelligence["severity"] == "CRITICAL"


def test_memory_intelligence_detects_significant_consumer():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    intelligence = result["memory_intelligence"]

    assert intelligence["is_significant_consumer"] is True


def test_analyzer_builds_memory_finding():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_finding" in result


def test_memory_finding_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis["total_findings"] >= 1


def test_memory_finding_affects_overall_status():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert result["diagnosis"]["status"] == "CRITICAL"

