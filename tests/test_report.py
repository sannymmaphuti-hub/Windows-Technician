from diagnostics.report import generate_report


def create_test_data():

    system_info = {
        "computer_name": "TEST-PC",
        "operating_system": "Windows",
        "os_version": "10.0",
        "architecture": "AMD64",
        "processor": "Test Processor"
    }

    cpu_diagnostics = {
        "status": "HEALTHY",
        "findings": [],
        "recommendation": "No immediate CPU action is required."
    }

    memory_diagnostics = {
        "status": "HEALTHY",
        "findings": [],
        "recommendation": "No immediate memory action is required."
    }

    network_diagnostics = {
        "active_adapter": None,
        "gateway": None,
        "gateway_reachable": False,
        "internet_reachable": True,
        "dns_working": True,
        "findings": []
    }

    system_health = {
        "status": "HEALTHY",
        "findings": []
    }

    return {
        "system_info": system_info,
        "cpu_diagnostics": cpu_diagnostics,
        "memory_diagnostics": memory_diagnostics,
        "process_findings": [],
        "process_persistence_findings": [],
        "process_behavior_findings": [],
        "network_diagnostics": network_diagnostics,
        "gpu_info": [],
        "gpu_findings": [],
        "gpu_recommendations": [],
        "storage_info": [],
        "storage_diagnostics": [],
        "system_health": system_health,
        "root_cause_candidates": [],
        "system_recommendations": [
            "No immediate system action is required."
        ],
        "correlation_findings": [],
        "prioritized_issues": [],
        "primary_issue": None
    }


def test_report_generation():

    data = create_test_data()

    report = generate_report(
        data["system_info"],
        data["cpu_diagnostics"],
        data["memory_diagnostics"],
        data["process_findings"],
        data["process_persistence_findings"],
        data["process_behavior_findings"],
        data["network_diagnostics"],
        data["gpu_info"],
        data["gpu_findings"],
        data["gpu_recommendations"],
        data["storage_info"],
        data["storage_diagnostics"],
        data["system_health"],
        data["root_cause_candidates"],
        data["system_recommendations"],
        data["correlation_findings"],
        data["prioritized_issues"],
        data["primary_issue"]
    )

    assert isinstance(report, str)
    assert len(report) > 0


def test_report_contains_system_information():

    data = create_test_data()

    report = generate_report(
        data["system_info"],
        data["cpu_diagnostics"],
        data["memory_diagnostics"],
        data["process_findings"],
        data["process_persistence_findings"],
        data["process_behavior_findings"],
        data["network_diagnostics"],
        data["gpu_info"],
        data["gpu_findings"],
        data["gpu_recommendations"],
        data["storage_info"],
        data["storage_diagnostics"],
        data["system_health"],
        data["root_cause_candidates"],
        data["system_recommendations"],
        data["correlation_findings"],
        data["prioritized_issues"],
        data["primary_issue"]
    )

    assert "TEST-PC" in report
    assert "Windows" in report
    assert "AMD64" in report


def test_report_contains_major_sections():

    data = create_test_data()

    report = generate_report(
        data["system_info"],
        data["cpu_diagnostics"],
        data["memory_diagnostics"],
        data["process_findings"],
        data["process_persistence_findings"],
        data["process_behavior_findings"],
        data["network_diagnostics"],
        data["gpu_info"],
        data["gpu_findings"],
        data["gpu_recommendations"],
        data["storage_info"],
        data["storage_diagnostics"],
        data["system_health"],
        data["root_cause_candidates"],
        data["system_recommendations"],
        data["correlation_findings"],
        data["prioritized_issues"],
        data["primary_issue"]
    )

    assert "CPU DIAGNOSTICS" in report
    assert "MEMORY DIAGNOSTICS" in report
    assert "SYSTEM HEALTH" in report