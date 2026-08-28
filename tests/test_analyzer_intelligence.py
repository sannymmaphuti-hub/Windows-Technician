from engine.analyzer import Analyzer


class FakeCollector:

    category = "PROCESS"

    def collect(self):

        return {
            "processes": [
                {
                    "pid": 1234,
                    "name": "test.exe",
                    "cpu_percent": 95.0,
                    "memory_mb": 100.0,
                    "status": "running"
                }
            ]
        }


def test_analyzer_has_process_intelligence():

    analyzer = Analyzer()

    assert analyzer.intelligence is not None


def test_analyzer_can_use_process_intelligence():

    analyzer = Analyzer(
        collectors=[
            FakeCollector()
        ]
    )

    assert analyzer.intelligence is not None

def test_analyzer_uses_explicit_process_collector():

    process_collector = FakeCollector()

    analyzer = Analyzer(
        collectors=[
            process_collector
        ],
        process_collector=process_collector
    )

    assert analyzer.process_collector is process_collector