# ==========================================================
# WINDOWS TECHNICIAN v0.1
# SYSTEM HEALTH ANALYZER
# ==========================================================


def analyze_system_health(
    cpu_diagnostics,
    memory_diagnostics,
    storage_diagnostics,
    process_findings,
    process_persistence_findings,
    process_behavior_findings,
    network_diagnostics,
    correlation_findings
):

    findings = []
    statuses = []

    # ======================================================
    # CPU
    # ======================================================

    cpu_status = cpu_diagnostics["status"]

    if cpu_status == "CRITICAL":

        statuses.append("CRITICAL")

        findings.append({
            "severity": "CRITICAL",
            "category": "SYSTEM",
            "message": (
                "CPU utilization is currently a critical "
                "system concern."
            )
        })

    elif cpu_status == "WARNING":

        statuses.append("WARNING")

        findings.append({
            "severity": "WARNING",
            "category": "SYSTEM",
            "message": (
                "CPU utilization is elevated "
                "and requires investigation."
            )
        })

    else:

        statuses.append("HEALTHY")

        findings.append({
            "severity": "INFO",
            "category": "SYSTEM",
            "message": (
                "CPU utilization is currently "
                "within a healthy range."
            )
        })

    # ======================================================
    # MEMORY
    # ======================================================

    memory_status = memory_diagnostics["status"]

    if memory_status == "CRITICAL":

        statuses.append("CRITICAL")

        findings.append({
            "severity": "CRITICAL",
            "category": "SYSTEM",
            "message": (
                "Memory pressure is currently "
                "a critical system concern."
            )
        })

    elif memory_status == "HIGH MEMORY PRESSURE":

        statuses.append("WARNING")

        findings.append({
            "severity": "WARNING",
            "category": "SYSTEM",
            "message": (
                "Memory pressure is currently high "
                "and requires attention."
            )
        })

    elif memory_status == "WARNING":

        statuses.append("WARNING")

        findings.append({
            "severity": "WARNING",
            "category": "SYSTEM",
            "message": (
                "Memory usage is elevated "
                "and should be monitored."
            )
        })

    elif memory_status == "ATTENTION":

        statuses.append("ATTENTION")

        findings.append({
            "severity": "INFO",
            "category": "SYSTEM",
            "message": (
                "Memory usage is moderately elevated."
            )
        })

    else:

        statuses.append("HEALTHY")

        findings.append({
            "severity": "INFO",
            "category": "SYSTEM",
            "message": (
                "Memory utilization is currently "
                "within an acceptable range."
            )
        })

    # ======================================================
    # STORAGE
    # ======================================================

    for storage in storage_diagnostics:

        storage_status = storage["status"]

        if storage_status == "CRITICAL":

            statuses.append("CRITICAL")

            findings.append({
                "severity": "CRITICAL",
                "category": "SYSTEM",
                "message": (
                    f"Storage capacity on "
                    f"{storage['drive']} is critically low."
                )
            })

        elif storage_status == "WARNING":

            statuses.append("WARNING")

            findings.append({
                "severity": "WARNING",
                "category": "SYSTEM",
                "message": (
                    f"Storage capacity on "
                    f"{storage['drive']} is very high."
                )
            })

        elif storage_status == "ATTENTION":

            statuses.append("ATTENTION")

            findings.append({
                "severity": "INFO",
                "category": "SYSTEM",
                "message": (
                    f"Storage usage on "
                    f"{storage['drive']} is elevated."
                )
            })

        else:

            statuses.append("HEALTHY")

            findings.append({
                "severity": "INFO",
                "category": "SYSTEM",
                "message": (
                    f"Storage capacity on "
                    f"{storage['drive']} is healthy."
                )
            })

    # ======================================================
    # PROCESS DIAGNOSTICS
    # ======================================================

    for finding in process_findings:

        severity = finding["severity"]

        if severity == "CRITICAL":

            statuses.append("CRITICAL")

            findings.append({
                "severity": "CRITICAL",
                "category": "PROCESS",
                "message": (
                    f"Process issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "WARNING":

            statuses.append("WARNING")

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS",
                "message": (
                    f"Process issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "INFO":

            findings.append({
                "severity": "INFO",
                "category": "PROCESS",
                "message": (
                    f"Process observation: "
                    f"{finding['message']}"
                )
            })

    # ======================================================
    # PROCESS PERSISTENCE
    # ======================================================

    for finding in process_persistence_findings:

        severity = finding["severity"]

        if severity == "CRITICAL":

            statuses.append("CRITICAL")

            findings.append({
                "severity": "CRITICAL",
                "category": "PROCESS PERSISTENCE",
                "message": (
                    f"Persistent process issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "WARNING":

            statuses.append("WARNING")

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS PERSISTENCE",
                "message": (
                    f"Persistent process issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "INFO":

            findings.append({
                "severity": "INFO",
                "category": "PROCESS PERSISTENCE",
                "message": (
                    f"Persistent process observation: "
                    f"{finding['message']}"
                )
            })

    # ======================================================
    # PROCESS CPU BEHAVIOR
    # ======================================================

    for finding in process_behavior_findings:

        severity = finding["severity"]

        if severity == "CRITICAL":

            statuses.append("CRITICAL")

            findings.append({
                "severity": "CRITICAL",
                "category": "PROCESS CPU BEHAVIOR",
                "message": (
                    f"Process CPU behavior issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "WARNING":

            statuses.append("WARNING")

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS CPU BEHAVIOR",
                "message": (
                    f"Process CPU behavior issue detected: "
                    f"{finding['message']}"
                )
            })

        elif severity == "INFO":

            findings.append({
                "severity": "INFO",
                "category": "PROCESS CPU BEHAVIOR",
                "message": (
                    f"Process CPU behavior observed: "
                    f"{finding['message']}"
                )
            })

    # ======================================================
    # NETWORK
    # ======================================================

    network_findings = network_diagnostics.get("findings", [])

    network_status = "HEALTHY"

    if (
        not network_diagnostics.get("internet_reachable", False)
        and not network_diagnostics.get("dns_working", False)
    ):

        network_status = "CRITICAL"

    elif (
        not network_diagnostics.get("internet_reachable", False)
        or not network_diagnostics.get("dns_working", False)
    ):

        network_status = "WARNING"

    elif not network_diagnostics.get("gateway_reachable", False):

        # A missing gateway does not automatically mean
        # network failure if Internet and DNS are working.
        if (
            network_diagnostics.get("internet_reachable", False)
            and network_diagnostics.get("dns_working", False)
        ):
            network_status = "HEALTHY"

        else:
            network_status = "WARNING"

    if network_status == "CRITICAL":

        statuses.append("CRITICAL")

        findings.append({
            "severity": "CRITICAL",
            "category": "NETWORK",
            "message": (
                "Network connectivity is currently "
                "a critical system concern."
            )
        })

    elif network_status == "WARNING":

        statuses.append("WARNING")

        findings.append({
            "severity": "WARNING",
            "category": "NETWORK",
            "message": (
                "Network connectivity is degraded "
                "and requires investigation."
            )
        })

    else:

        statuses.append("HEALTHY")

        findings.append({
            "severity": "INFO",
            "category": "NETWORK",
            "message": (
                "Network connectivity is currently "
                "healthy."
            )
        })


    # ======================================================
    # CROSS-DIAGNOSTIC CORRELATION
    # ======================================================

    for finding in correlation_findings:

        severity = finding["severity"]

        if severity == "CRITICAL":

            statuses.append("CRITICAL")

            findings.append({
                "severity": "CRITICAL",
                "category": "CROSS-DIAGNOSTIC CORRELATION",
                "message": (
                    f"{finding['relationship']}: "
                    f"{finding['message']}"
                )
            })

        elif severity == "WARNING":

            statuses.append("WARNING")

            findings.append({
                "severity": "WARNING",
                "category": "CROSS-DIAGNOSTIC CORRELATION",
                "message": (
                    f"{finding['relationship']}: "
                    f"{finding['message']}"
                )
            })

        elif severity == "INFO":

            findings.append({
                "severity": "INFO",
                "category": "CROSS-DIAGNOSTIC CORRELATION",
                "message": (
                    f"{finding['relationship']}: "
                    f"{finding['message']}"
                )
            })

    # ======================================================
    # OVERALL SYSTEM STATUS
    # ======================================================

    if "CRITICAL" in statuses:

        overall_status = "CRITICAL"

    elif "WARNING" in statuses:

        overall_status = "WARNING"

    elif "ATTENTION" in statuses:

        overall_status = "ATTENTION"

    else:

        overall_status = "HEALTHY"

    return {
        "status": overall_status,
        "findings": findings
    }


# ==========================================================
# SYSTEM RECOMMENDATIONS
# ==========================================================


def generate_system_recommendation(
    findings,
    overall_status
):

    if overall_status == "CRITICAL":

        return [
            "Address critical system findings immediately.",
            "Investigate the primary resource under critical pressure.",
            "Reduce unnecessary resource consumption."
        ]

    elif overall_status == "WARNING":

        return [
            "Investigate warning-level system findings.",
            "Monitor CPU, memory, and storage usage.",
            "Take corrective action if resource usage continues increasing."
        ]

    elif overall_status == "ATTENTION":

        return [
            "Monitor elevated system resource usage.",
            "Investigate the affected resource if the condition persists."
        ]

    else:

        return [
            "No immediate system action is required.",
            "Continue monitoring system resource usage."
        ]

# ==========================================================
# PRIMARY ISSUE ANALYZER
# ==========================================================


def identify_primary_issue(
    cpu_diagnostics,
    memory_diagnostics,
    storage_diagnostics,
    process_findings,
    process_persistence_findings,
    process_behavior_findings,
    network_diagnostics,
    correlation_findings
):
    """
    Identify the most important current system issue.

    The function prioritizes diagnostic findings by
    severity and diagnostic importance.

    It does not claim that the selected issue is the
    root cause. It identifies the most significant
    observed problem.
    """

    candidates = []

    # ======================================================
    # CPU
    # ======================================================

    cpu_status = cpu_diagnostics.get("status")

    if cpu_status == "CRITICAL":

        candidates.append({
            "severity": "CRITICAL",
            "category": "CPU",
            "issue": "Critical CPU utilization",
            "reason": (
                "CPU diagnostics indicate critically "
                "high CPU utilization."
            )
        })

    elif cpu_status == "WARNING":

        candidates.append({
            "severity": "WARNING",
            "category": "CPU",
            "issue": "Elevated CPU utilization",
            "reason": (
                "CPU diagnostics indicate elevated "
                "CPU utilization."
            )
        })

    # ======================================================
    # MEMORY
    # ======================================================

    memory_status = memory_diagnostics.get("status")

    if memory_status == "CRITICAL":

        candidates.append({
            "severity": "CRITICAL",
            "category": "MEMORY",
            "issue": "Critical memory pressure",
            "reason": (
                "System memory is under critical pressure."
            )
        })

    elif memory_status in (
        "WARNING",
        "HIGH MEMORY PRESSURE"
    ):

        candidates.append({
            "severity": "WARNING",
            "category": "MEMORY",
            "issue": "Elevated memory utilization",
            "reason": (
                "System memory usage is elevated "
                "and may affect responsiveness."
            )
        })

    elif memory_status == "ATTENTION":

        candidates.append({
            "severity": "ATTENTION",
            "category": "MEMORY",
            "issue": "Moderately elevated memory utilization",
            "reason": (
                "Memory usage is moderately elevated."
            )
        })

    # ======================================================
    # STORAGE
    # ======================================================

    for storage in storage_diagnostics:

        status = storage.get("status")
        drive = storage.get("drive", "Unknown drive")

        if status == "CRITICAL":

            candidates.append({
                "severity": "CRITICAL",
                "category": "STORAGE",
                "issue": (
                    f"Critically low storage on {drive}"
                ),
                "reason": (
                    f"Available storage on {drive} "
                    f"is critically low."
                )
            })

        elif status == "WARNING":

            candidates.append({
                "severity": "WARNING",
                "category": "STORAGE",
                "issue": (
                    f"High storage usage on {drive}"
                ),
                "reason": (
                    f"Storage usage on {drive} "
                    f"is approaching a concerning level."
                )
            })

        elif status == "ATTENTION":

            candidates.append({
                "severity": "ATTENTION",
                "category": "STORAGE",
                "issue": (
                    f"Elevated storage usage on {drive}"
                ),
                "reason": (
                    f"Storage usage on {drive} "
                    f"is elevated."
                )
            })

    # ======================================================
    # PROCESS FINDINGS
    # ======================================================

    for finding in process_findings:

        severity = finding.get("severity")

        if severity in (
            "CRITICAL",
            "WARNING"
        ):

            candidates.append({
                "severity": severity,
                "category": "PROCESS",
                "issue": "Abnormal process activity",
                "reason": finding.get(
                    "message",
                    "A process reported abnormal activity."
                )
            })

    # ======================================================
    # PROCESS PERSISTENCE
    # ======================================================

    for finding in process_persistence_findings:

        severity = finding.get("severity")

        if severity in (
            "CRITICAL",
            "WARNING"
        ):

            candidates.append({
                "severity": severity,
                "category": "PROCESS PERSISTENCE",
                "issue": "Persistent process activity",
                "reason": finding.get(
                    "message",
                    "Persistent process activity was detected."
                )
            })

    # ======================================================
    # CPU BEHAVIOR
    # ======================================================

    for finding in process_behavior_findings:

        severity = finding.get("severity")

        if severity in (
            "CRITICAL",
            "WARNING"
        ):

            candidates.append({
                "severity": severity,
                "category": "CPU BEHAVIOR",
                "issue": "Abnormal CPU process behavior",
                "reason": finding.get(
                    "message",
                    "Abnormal CPU behavior was detected."
                )
            })

    # ======================================================
    # NETWORK
    # ======================================================

    internet_reachable = network_diagnostics.get(
        "internet_reachable",
        False
    )

    dns_working = network_diagnostics.get(
        "dns_working",
        False
    )

    gateway_reachable = network_diagnostics.get(
        "gateway_reachable",
        False
    )

    if not internet_reachable and not dns_working:

        candidates.append({
            "severity": "CRITICAL",
            "category": "NETWORK",
            "issue": "Network connectivity failure",
            "reason": (
                "Internet connectivity and DNS resolution "
                "are both unavailable."
            )
        })

    elif not internet_reachable or not dns_working:

        candidates.append({
            "severity": "WARNING",
            "category": "NETWORK",
            "issue": "Degraded network connectivity",
            "reason": (
                "Network connectivity or DNS resolution "
                "is not functioning normally."
            )
        })

    elif not gateway_reachable:

        candidates.append({
            "severity": "WARNING",
            "category": "NETWORK",
            "issue": "Default gateway is unreachable",
            "reason": (
                "The configured default gateway could "
                "not be reached."
            )
        })

    # ======================================================
    # CROSS-DIAGNOSTIC CORRELATIONS
    # ======================================================

    for finding in correlation_findings:

        severity = finding.get("severity")

        if severity in (
            "CRITICAL",
            "WARNING"
        ):

            candidates.append({
                "severity": severity,
                "category": "CORRELATION",
                "issue": (
                    finding.get(
                        "relationship",
                        "Cross-diagnostic issue"
                    )
                ),
                "reason": finding.get(
                    "message",
                    "Multiple diagnostic signals "
                    "appear to be related."
                )
            })

    # ======================================================
    # NO PROBLEMS
    # ======================================================

    if not candidates:

        return {
            "status": "HEALTHY",
            "category": "SYSTEM",
            "issue": "No significant system issue detected.",
            "severity": "INFO",
            "reason": (
                "Current diagnostic results do not "
                "indicate a significant system problem."
            )
        }

    # ======================================================
    # SEVERITY PRIORITY
    # ======================================================

    severity_priority = {
        "CRITICAL": 3,
        "WARNING": 2,
        "ATTENTION": 1,
        "INFO": 0
    }

    # ======================================================
    # SELECT PRIMARY ISSUE
    # ======================================================

    primary_issue = max(
        candidates,
        key=lambda candidate: severity_priority.get(
            candidate["severity"],
            0
        )
    )

    return {
        "status": primary_issue["severity"],
        "category": primary_issue["category"],
        "issue": primary_issue["issue"],
        "severity": primary_issue["severity"],
        "reason": primary_issue["reason"]
    }

# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    test_cpu = {
        "status": "HEALTHY"
    }

    test_memory = {
        "status": "HIGH MEMORY PRESSURE"
    }

    test_storage = [
        {
            "drive": "C:\\",
            "status": "HEALTHY"
        }
    ]

    test_process_findings = []

    test_process_persistence_findings = []

    test_process_behavior_findings = [
        {
            "severity": "INFO",
            "name": "MemCompression",
            "classification": "CPU SPIKE",
            "message": (
                "MemCompression experienced "
                "temporary high CPU activity."
            )
        }
    ]

    test_correlation_findings = [
        {
            "severity": "INFO",
            "category": "CROSS-DIAGNOSTIC CORRELATION",
            "relationship": "MEMORY PRESSURE + CPU SPIKE",
            "process": "MemCompression",
            "message": (
                "High memory pressure coincided "
                "with temporary CPU activity from "
                "MemCompression."
            )
        }
    ]

    test_network_diagnostics = {
        "internet_reachable": True,
        "dns_working": True,
        "gateway_reachable": True,
        "findings": []
    }


    result = analyze_system_health(
        test_cpu,
        test_memory,
        test_storage,
        test_process_findings,
        test_process_persistence_findings,
        test_process_behavior_findings,
        test_network_diagnostics,
        test_correlation_findings
    )

    print("==========================================")
    print("SYSTEM HEALTH TEST")
    print("==========================================")

    print(f"Overall Status : {result['status']}")

    print()
    print("System Findings")
    print("------------------------------------------")

    for finding in result["findings"]:

        print(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    recommendations = generate_system_recommendation(
        result["findings"],
        result["status"]
    )

    print()
    print("System Recommendations")
    print("------------------------------------------")

    for recommendation in recommendations:

        print(f"- {recommendation}")