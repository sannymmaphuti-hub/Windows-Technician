# ==========================================
# WINDOWS TECHNICIAN v0.2
# PROCESS INTELLIGENCE INTEGRATION TESTS
# ==========================================

from engine.analyzer import Analyzer


class FakeCPUCollector:

    category = "CPU"

    def collect(self):

        return {
            "usage_percent": 95.0
        }


class FakeProcessCollector:

    category = "PROCESS"

    def collect(self):

        return {
            "processes": [
                {
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 85.0,
                    "memory_mb": 500.0,
                    "status": "running"
                },
                {
                    "pid": 5678,
                    "name": "code.exe",
                    "cpu_percent": 20.0,
                    "memory_mb": 300.0,
                    "status": "running"
                }
            ]
        }


def test_analyzer_runs_process_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "intelligence" in result


def test_process_intelligence_identifies_top_process():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    intelligence = result["intelligence"]

    assert intelligence["name"] == "chrome.exe"
    assert intelligence["pid"] == 1234
    assert intelligence["severity"] == "CRITICAL"


def test_process_intelligence_detects_significant_contributor():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    intelligence = result["intelligence"]

    assert intelligence["is_significant_contributor"] is True

def test_analyzer_builds_process_finding():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "process_finding" in result

    finding = result["process_finding"]

    assert finding["category"] == "PROCESS"
    assert finding["process"] == "chrome.exe"
    assert finding["pid"] == 1234


def test_process_finding_preserves_intelligence_severity():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["process_finding"]

    assert finding["severity"] == "CRITICAL"


def test_process_finding_preserves_contributor_status():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    finding = result["process_finding"]

    assert finding["is_significant_contributor"] is True

def test_process_finding_enters_diagnosis():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis["total_findings"] == 1


def test_process_finding_appears_in_diagnosis_findings():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    findings = result["diagnosis"]["findings"]

    assert len(findings) == 1
    assert findings[0]["category"] == "PROCESS"
    assert findings[0]["process"] == "chrome.exe"


def test_process_finding_affects_overall_status():

    analyzer = Analyzer(
        collectors=[
            FakeCPUCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert result["diagnosis"]["status"] == "CRITICAL"