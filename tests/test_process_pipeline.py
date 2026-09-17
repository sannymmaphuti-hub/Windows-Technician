# ==========================================
# Windows Technician v0.5
# PROCESS INTELLIGENCE PIPELINE TESTS
# ==========================================


from engine.intelligence.process_pipeline import (
    ProcessIntelligencePipeline
)


def test_process_pipeline_identifies_top_process():

    pipeline = ProcessIntelligencePipeline()

    result = pipeline.analyze(

        cpu_evidence={
            "usage_percent": 95.0
        },

        process_evidence={
            "processes": [
                {
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 85.0
                },
                {
                    "pid": 5678,
                    "name": "code.exe",
                    "cpu_percent": 20.0
                }
            ]
        },

        process_cpu_history=[]
    )

    assert result["intelligence"] is not None

    assert (
        result["intelligence"]["name"]
        == "chrome.exe"
    )


def test_process_pipeline_builds_finding():

    pipeline = ProcessIntelligencePipeline()

    result = pipeline.analyze(

        cpu_evidence={
            "usage_percent": 95.0
        },

        process_evidence={
            "processes": [
                {
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 85.0
                }
            ]
        },

        process_cpu_history=[]
    )

    finding = result["finding"]

    assert finding is not None

    assert finding["category"] == "PROCESS"

    assert finding["process"] == "chrome.exe"

    assert finding["pid"] == 1234


def test_process_pipeline_uses_cpu_history():

    pipeline = ProcessIntelligencePipeline()

    result = pipeline.analyze(

        cpu_evidence={
            "usage_percent": 95.0
        },

        process_evidence={
            "processes": [
                {
                    "pid": 1234,
                    "name": "chrome.exe",
                    "cpu_percent": 85.0
                }
            ]
        },

        process_cpu_history=[
            {
                "pid": 1234,
                "name": "chrome.exe",
                "samples": [
                    82.0,
                    85.0,
                    88.0,
                    91.0,
                    87.0
                ]
            }
        ]
    )

    intelligence = result["intelligence"]

    assert intelligence["behavior"] == "PERSISTENT"

    assert (
        intelligence["persistence_ratio"]
        == 100.0
    )


def test_process_pipeline_handles_missing_cpu():

    pipeline = ProcessIntelligencePipeline()

    result = pipeline.analyze(

        cpu_evidence={},

        process_evidence={
            "processes": []
        }
    )

    assert result["intelligence"] is None

    assert result["finding"] is None


def test_process_pipeline_handles_missing_processes():

    pipeline = ProcessIntelligencePipeline()

    result = pipeline.analyze(

        cpu_evidence={
            "usage_percent": 90.0
        },

        process_evidence={}
    )

    assert result["intelligence"] is None

    assert result["finding"] is None

