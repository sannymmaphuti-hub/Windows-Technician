from diagnostics.correlation_analyzer import (
    correlate_memory_and_cpu_behavior
)


def test_no_correlation():
    memory_diagnostics = {
        "status": "NORMAL",
        "findings": []
    }

    process_behavior_findings = []

    result = correlate_memory_and_cpu_behavior(
        memory_diagnostics,
        process_behavior_findings
    )

    assert isinstance(result, list)

    assert len(result) == 0


def test_memory_cpu_correlation():
    memory_diagnostics = {
        "status": "HIGH MEMORY PRESSURE",
        "findings": [
            {
                "severity": "WARNING",
                "category": "MEMORY",
                "message": "High memory pressure detected."
            }
        ]
    }

    process_behavior_findings = [
        {
            "name": "MemCompression",
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "classification": "CPU SPIKE",
            "message": (
                "MemCompression experienced "
                "temporary high CPU activity."
            )
        }
    ]

    result = correlate_memory_and_cpu_behavior(
        memory_diagnostics,
        process_behavior_findings
    )

    assert isinstance(result, list)

    assert len(result) == 1

    assert result[0]["severity"] == "INFO"

    assert result[0]["category"] == (
        "CROSS-DIAGNOSTIC CORRELATION"
    )

    assert result[0]["relationship"] == (
        "MEMORY PRESSURE + CPU SPIKE"
    )

    assert result[0]["process"] == "MemCompression"


def test_correlation_structure():
    memory_diagnostics = {
        "status": "WARNING",
        "findings": [
            {
                "severity": "WARNING",
                "category": "MEMORY",
                "message": "Memory usage is high."
            }
        ]
    }

    process_behavior_findings = [
        {
            "name": "MemCompression",
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "classification": "CPU SPIKE",
            "message": (
                "Temporary CPU activity detected."
            )
        }
    ]

    result = correlate_memory_and_cpu_behavior(
        memory_diagnostics,
        process_behavior_findings
    )

    assert isinstance(result, list)

    assert len(result) == 1

    finding = result[0]

    assert "severity" in finding
    assert "category" in finding
    assert "relationship" in finding
    assert "process" in finding
    assert "message" in finding