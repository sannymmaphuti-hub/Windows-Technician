from diagnostics.analyzer import (
    analyze_memory_consumers,
    analyze_resource_correlation,
    identify_root_cause_candidates
)


def test_analyze_memory_consumers():
    memory_by_application = [
        {
            "name": "Code.exe",
            "process_count": 3,
            "memory_mb": 900.0
        },
        {
            "name": "chrome.exe",
            "process_count": 5,
            "memory_mb": 500.0
        }
    ]

    result = analyze_memory_consumers(
        memory_by_application
    )

    assert isinstance(result, list)

    assert len(result) > 0

    assert result[0]["name"] == "Code.exe"


def test_analyze_resource_correlation():
    memory_info = {
        "total_gb": 8.0,
        "used_gb": 7.2,
        "available_gb": 0.8,
        "usage_percent": 90.0
    }

    top_memory_consumers = [
        {
            "name": "Code.exe",
            "process_count": 3,
            "memory_mb": 900.0
        }
    ]

    top_cpu_processes = [
        {
            "pid": 1234,
            "name": "Code.exe",
            "cpu_percent": 35.0
        }
    ]

    result = analyze_resource_correlation(
        memory_info,
        top_memory_consumers,
        top_cpu_processes
    )

    assert isinstance(result, list)


def test_identify_root_cause_candidates():
    memory_info = {
        "total_gb": 8.0,
        "used_gb": 7.2,
        "available_gb": 0.8,
        "usage_percent": 90.0
    }

    top_memory_consumers = [
        {
            "name": "Code.exe",
            "process_count": 3,
            "memory_mb": 900.0
        }
    ]

    top_cpu_processes = [
        {
            "pid": 1234,
            "name": "Code.exe",
            "cpu_percent": 35.0
        }
    ]

    result = identify_root_cause_candidates(
        memory_info,
        top_memory_consumers,
        top_cpu_processes
    )

    assert isinstance(result, list)

    for candidate in result:

        assert "problem" in candidate
        assert "likely_source" in candidate
        assert "confidence" in candidate
        assert "evidence" in candidate
        assert "recommendation" in candidate