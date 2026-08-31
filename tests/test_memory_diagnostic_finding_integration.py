# ==========================================
# Windows Technician v0.3
# MEMORY DIAGNOSTIC FINDING INTEGRATION TESTS
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


def test_analyzer_contains_memory_diagnostic_finding():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "memory_diagnostic_finding" in result


def test_memory_diagnostic_finding_has_memory_category():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["memory_diagnostic_finding"]

    assert finding["category"] == "MEMORY"


def test_memory_diagnostic_finding_preserves_severity():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["memory_diagnostic_finding"]

    assert finding["severity"] in (
        "CRITICAL",
        "WARNING",
        "INFO"
    )


def test_memory_diagnostic_finding_preserves_process():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["memory_diagnostic_finding"]

    assert finding["process"] == "chrome.exe"
    assert finding["pid"] == 1234


def test_memory_diagnostic_finding_preserves_diagnostic_message():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["memory_diagnostic_finding"]

    assert finding["message"] != ""


def test_memory_diagnostic_finding_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis is not None
