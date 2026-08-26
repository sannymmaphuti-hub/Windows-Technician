from diagnostics.memory import generate_memory_diagnostics


def test_memory_normal():
    memory_info = {
        "total_gb": 8.0,
        "used_gb": 4.0,
        "available_gb": 4.0,
        "usage_percent": 50.0
    }

    memory_by_application = []

    result = generate_memory_diagnostics(
        memory_info,
        memory_by_application
    )

    assert result["status"] == "NORMAL"


def test_memory_high_pressure():
    memory_info = {
        "total_gb": 8.0,
        "used_gb": 7.2,
        "available_gb": 0.8,
        "usage_percent": 90.0
    }

    memory_by_application = []

    result = generate_memory_diagnostics(
        memory_info,
        memory_by_application
    )

    assert result["status"] == "HIGH MEMORY PRESSURE"

def test_memory_critical():
    memory_info = {
        "total_gb": 8.0,
        "used_gb": 7.8,
        "available_gb": 0.2,
        "usage_percent": 98.0
    }

    memory_by_application = []

    result = generate_memory_diagnostics(
        memory_info,
        memory_by_application
    )

    assert result["status"] == "CRITICAL"