from diagnostics.cpu import generate_cpu_diagnostics


def test_cpu_healthy():
    cpu_info = {
        "usage_percent": 30.0,
        "status": "NORMAL"
    }

    top_processes = []

    result = generate_cpu_diagnostics(
        cpu_info,
        top_processes
    )

    assert result["status"] == "HEALTHY"


def test_cpu_warning():
    cpu_info = {
        "usage_percent": 80.0,
        "status": "WARNING"
    }

    top_processes = []

    result = generate_cpu_diagnostics(
        cpu_info,
        top_processes
    )

    assert result["status"] == "WARNING"


def test_cpu_critical():
    cpu_info = {
        "usage_percent": 95.0,
        "status": "CRITICAL"
    }

    top_processes = []

    result = generate_cpu_diagnostics(
        cpu_info,
        top_processes
    )

    assert result["status"] == "CRITICAL"