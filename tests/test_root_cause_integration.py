# ==========================================
# Windows Technician v0.6
# ROOT CAUSE INTEGRATION TEST
# ==========================================

from engine.analyzer import Analyzer


class FakeCPUCollector:

    category = "CPU"

    def collect(self):

        return {
            "usage_percent": 90
        }


class FakeMemoryCollector:

    category = "MEMORY"

    def collect(self):

        return {
            "usage_percent": 85
        }


class FakeProcessCollector:

    category = "PROCESS"

    def collect(self):

        return {
            "processes": [
                {
                    "name": "MemCompression",
                    "pid": 1234,
                    "cpu_percent": 85,
                    "memory_mb": 1500
                }
            ]
        }


def test_analyzer_returns_correlations():

    analyzer = Analyzer(

        collectors=[
            FakeCPUCollector(),
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "correlations" in result

    assert isinstance(
        result["correlations"],
        list
    )


def test_analyzer_returns_root_cause_candidates():

    analyzer = Analyzer(

        collectors=[
            FakeCPUCollector(),
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "root_cause_candidates" in result

    assert isinstance(
        result["root_cause_candidates"],
        list
    )


def test_analyzer_returns_primary_root_cause():

    analyzer = Analyzer(

        collectors=[
            FakeCPUCollector(),
            FakeMemoryCollector(),
            FakeProcessCollector()
        ]
    )

    result = analyzer.analyze()

    assert "primary_root_cause" in result
