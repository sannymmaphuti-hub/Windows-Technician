from diagnostics.system_analyzer import (
    analyze_system_health,
    generate_system_recommendation
)


def test_system_health_healthy():

    cpu_diagnostics = {
        "status": "HEALTHY",
        "findings": []
    }

    memory_diagnostics = {
        "status": "HEALTHY",
        "findings": []
    }

    storage_diagnostics = [
        {
            "drive": "C:\\",
            "status": "HEALTHY",
            "severity": "INFO",
            "finding": "Storage capacity is healthy."
        }
    ]

    process_findings = []

    process_persistence_findings = []

    process_behavior_findings = []

    network_diagnostics = {
        "internet_reachable": True,
        "dns_working": True,
        "findings": []
    }

    correlation_findings = []

    result = analyze_system_health(
        cpu_diagnostics,
        memory_diagnostics,
        storage_diagnostics,
        process_findings,
        process_persistence_findings,
        process_behavior_findings,
        network_diagnostics,
        correlation_findings
    )

    assert isinstance(result, dict)

    assert result["status"] == "HEALTHY"

    assert "findings" in result


def test_system_health_warning():

    cpu_diagnostics = {
        "status": "HEALTHY",
        "findings": []
    }

    memory_diagnostics = {
        "status": "WARNING",
        "findings": [
            {
                "severity": "WARNING",
                "category": "MEMORY",
                "message": "Memory usage is elevated."
            }
        ]
    }

    storage_diagnostics = [
        {
            "drive": "C:\\",
            "status": "HEALTHY",
            "severity": "INFO",
            "finding": "Storage capacity is healthy."
        }
    ]
    process_findings = []

    process_persistence_findings = []

    process_behavior_findings = []

    network_diagnostics = {
        "internet_reachable": True,
        "dns_working": True,
        "findings": []
    }

    correlation_findings = []

    result = analyze_system_health(
        cpu_diagnostics,
        memory_diagnostics,
        storage_diagnostics,
        process_findings,
        process_persistence_findings,
        process_behavior_findings,
        network_diagnostics,
        correlation_findings
    )

    assert isinstance(result, dict)

    assert result["status"] == "WARNING"

    assert "findings" in result


def test_generate_recommendations():

    findings = [
        {
            "severity": "WARNING",
            "category": "MEMORY",
            "message": "Memory usage is elevated."
        }
    ]

    recommendations = generate_system_recommendation(
        findings,
        "WARNING"
    )

    assert isinstance(
        recommendations,
        list
    )

    assert len(recommendations) > 0