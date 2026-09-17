# ==========================================
# Windows Technician v0.5
# MEMORY DIAGNOSTIC INTELLIGENCE INTEGRATION
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


def test_analyzer_runs_memory_diagnostic_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_diagnostic_intelligence" in result


def test_memory_diagnostic_intelligence_identifies_severity():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnostic = result[
        "memory_diagnostic_intelligence"
    ]

    assert diagnostic["severity"] in (
        "CRITICAL",
        "WARNING",
        "INFO"
    )


def test_memory_diagnostic_intelligence_preserves_process():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnostic = result[
        "memory_diagnostic_intelligence"
    ]

    assert diagnostic["name"] == "chrome.exe"
    assert diagnostic["pid"] == 1234


def test_memory_diagnostic_intelligence_reports_memory_usage():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnostic = result[
        "memory_diagnostic_intelligence"
    ]

    assert diagnostic["system_memory_percent"] == 92.0


def test_memory_diagnostic_intelligence_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis is not None


def test_memory_diagnostic_intelligence_produces_message():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnostic = result[
        "memory_diagnostic_intelligence"
    ]

    assert diagnostic["message"]

