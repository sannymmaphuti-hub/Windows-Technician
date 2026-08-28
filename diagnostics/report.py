# ==========================================
# WINDOWS TECHNICIAN v0.2
# DIAGNOSTIC REPORT GENERATOR
# ==========================================


def generate_report(
    system_info,
    cpu_diagnostics,
    memory_diagnostics,
    process_findings,
    process_persistence_findings,
    process_behavior_findings,
    network_diagnostics,
    gpu_info,
    gpu_findings,
    gpu_recommendations,
    storage_info,
    storage_diagnostics,
    system_health,
    root_cause_candidates,
    system_recommendations,
    correlation_findings,
    prioritized_issues,
    primary_issue

):

    report = []

    # ==========================================
    # REPORT HEADER
    # ==========================================

    report.append("==========================================")
    report.append("       WINDOWS TECHNICIAN v0.2")
    report.append("          DIAGNOSTIC REPORT")
    report.append("==========================================")
    report.append("")

    # ==========================================
    # SYSTEM INFORMATION
    # ==========================================

    report.append("SYSTEM INFORMATION")
    report.append("------------------------------------------")

    report.append(
        f"Computer Name : {system_info['computer_name']}"
    )

    report.append(
        f"Operating System : {system_info['operating_system']}"
    )

    report.append(
        f"OS Version : {system_info['os_version']}"
    )

    report.append(
        f"Architecture : {system_info['architecture']}"
    )

    report.append(
        f"Processor : {system_info['processor']}"
    )

    report.append("")

    # ==========================================
    # CPU DIAGNOSTICS
    # ==========================================

    report.append("CPU DIAGNOSTICS")
    report.append("------------------------------------------")

    report.append(
        f"Status : {cpu_diagnostics['status']}"
    )

    report.append("")

    for finding in cpu_diagnostics["findings"]:

        report.append(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    report.append("")

    report.append(
        f"Recommendation : "
        f"{cpu_diagnostics['recommendation']}"
    )

    report.append("")

    # ==========================================
    # MEMORY DIAGNOSTICS
    # ==========================================

    report.append("MEMORY DIAGNOSTICS")
    report.append("------------------------------------------")

    report.append(
        f"Status : {memory_diagnostics['status']}"
    )

    report.append("")

    for finding in memory_diagnostics["findings"]:

        report.append(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    report.append("")

    report.append(
        f"Recommendation : "
        f"{memory_diagnostics['recommendation']}"
    )

    report.append("")

    # ==========================================
    # NETWORK DIAGNOSTICS
    # ==========================================

    report.append("NETWORK DIAGNOSTICS")
    report.append("------------------------------------------")

    active_adapter = network_diagnostics["active_adapter"]

    report.append(
        f"Active Adapter : "
        f"{active_adapter['name'] if active_adapter else 'None'}"
    )

    report.append(
        f"Default Gateway : "
        f"{network_diagnostics['gateway'] or 'None'}"
    )

    report.append(
        f"Gateway Reachable : "
        f"{'YES' if network_diagnostics['gateway_reachable'] else 'NO'}"
    )

    report.append(
        f"Internet Reachable : "
        f"{'YES' if network_diagnostics['internet_reachable'] else 'NO'}"
    )

    report.append(
        f"DNS Working : "
        f"{'YES' if network_diagnostics['dns_working'] else 'NO'}"
    )

    report.append("")

    report.append("Network Findings")
    report.append("------------------------------------------")

    for finding in network_diagnostics["findings"]:

        report.append(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    report.append("")

    report.append("GPU DIAGNOSTICS")
    report.append("------------------------------------------")

    for gpu in gpu_info:
        report.append(f"GPU : {gpu['name']}")
        report.append(f"Memory : {gpu['memory']:.2f} GB")
        report.append(f"Driver : {gpu['driver']}")
        report.append(f"Status : {gpu['status']}")
        report.append("")

    for finding in gpu_findings:

        if isinstance(finding, dict):

            report.append(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

        else:

            report.append(
                str(finding)
            )

    report.append("")

    if gpu_recommendations:
        for recommendation in gpu_recommendations:
            report.append(f"Recommendation : {recommendation}")
    else:
        report.append("Recommendation : No immediate GPU action is required.")

    report.append("")


    # ==========================================
    # PROCESS DIAGNOSTICS
    # ==========================================

    report.append("PROCESS DIAGNOSTICS")
    report.append("------------------------------------------")

    if not process_findings:

        report.append(
            "No abnormal process behavior detected."
        )

    else:

        for finding in process_findings:

            report.append(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

    report.append("")

    # ==========================================
    # PERSISTENT CPU FINDINGS
    # ==========================================

    report.append("PERSISTENT CPU FINDINGS")
    report.append("------------------------------------------")

    if not process_persistence_findings:

        report.append(
            "No persistent high CPU activity detected."
        )

    else:

        for finding in process_persistence_findings:

            report.append(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

            if "average_cpu_percent" in finding:

                report.append(
                    f"    Average CPU : "
                    f"{finding['average_cpu_percent']:.1f}%"
                )

            if "high_cpu_samples" in finding:

                report.append(
                    f"    High CPU Samples : "
                    f"{finding['high_cpu_samples']}/"
                    f"{finding['total_samples']}"
                )

    report.append("")

    # ==========================================
    # CPU BEHAVIOR FINDINGS
    # ==========================================

    report.append("CPU BEHAVIOR FINDINGS")
    report.append("------------------------------------------")

    if not process_behavior_findings:

        report.append(
            "No abnormal CPU behavior detected."
        )

    else:

        for finding in process_behavior_findings:

            report.append(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

            if "classification" in finding:

                report.append(
                    f"    Classification : "
                    f"{finding['classification']}"
                )

    report.append("")

    # ==========================================
    # CROSS-DIAGNOSTIC CORRELATIONS
    # ==========================================

    report.append("CROSS-DIAGNOSTIC CORRELATIONS")
    report.append("------------------------------------------")

    if not correlation_findings:

        report.append(
            "No cross-diagnostic relationships detected."
        )

    else:

        for finding in correlation_findings:

            report.append(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['relationship']}"
            )

            report.append(
                f"    Process : "
                f"{finding.get('process', 'N/A')}"
            )

            report.append(
                f"    Message : "
                f"{finding['message']}"
            )

    report.append("")

    # ==========================================
    # STORAGE DIAGNOSTICS
    # ==========================================

    report.append("STORAGE DIAGNOSTICS")
    report.append("------------------------------------------")

    if not storage_info:

        report.append(
            "No storage devices detected."
        )

    else:

        for drive in storage_info:

            report.append(
                f"Drive : {drive['device']}"
            )

            report.append(
                f"Mount Point : {drive['mountpoint']}"
            )

            report.append(
                f"File System : {drive['filesystem']}"
            )

            report.append(
                f"Total Space : {drive['total_gb']:.2f} GB"
            )

            report.append(
                f"Used Space : {drive['used_gb']:.2f} GB"
            )

            report.append(
                f"Free Space : {drive['free_gb']:.2f} GB"
            )

            report.append(
                f"Usage : {drive['usage_percent']:.1f}%"
            )

            diagnostic = None

            for item in storage_diagnostics:

                if item["drive"] == drive["mountpoint"]:

                    diagnostic = item
                    break

            if diagnostic:

                report.append(
                    f"Status : {diagnostic['status']}"
                )

                report.append("")

                report.append(
                    f"[{diagnostic['severity']}] "
                    f"STORAGE : "
                    f"{diagnostic['finding']}"
                )

                report.append("")

                report.append(
                    f"Recommendation : "
                    f"{diagnostic['recommendation']}"
                )

            else:

                report.append(
                    "Status : UNKNOWN"
                )

            report.append("")

    # ==========================================
    # ROOT-CAUSE ANALYSIS
    # ==========================================

    report.append("ROOT-CAUSE ANALYSIS")
    report.append("------------------------------------------")

    if not root_cause_candidates:

        report.append(
            "No root-cause candidates identified."
        )

    else:

        for candidate in root_cause_candidates:

            report.append(
                f"Problem : "
                f"{candidate['problem']}"
            )

            report.append(
                f"Likely Source : "
                f"{candidate['likely_source']}"
            )

            report.append(
                f"Confidence : "
                f"{candidate['confidence']}%"
            )

            report.append("Evidence :")

            for evidence in candidate["evidence"]:

                report.append(
                    f"    - {evidence}"
                )

            report.append(
                f"Recommendation : "
                f"{candidate['recommendation']}"
            )

            report.append("")

    # ==========================================
    # SYSTEM HEALTH
    # ==========================================

    report.append("SYSTEM HEALTH")
    report.append("------------------------------------------")

    report.append(
        f"Overall Status : "
        f"{system_health['status']}"
    )

    report.append("")

    for finding in system_health["findings"]:

        report.append(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    report.append("")

    # ==========================================
    # SYSTEM RECOMMENDATIONS
    # ==========================================

    report.append("SYSTEM RECOMMENDATIONS")
    report.append("------------------------------------------")

    if not system_recommendations:

        report.append(
            "No additional system recommendations."
        )

    else:

        for recommendation in system_recommendations:

            report.append(
                f"- {recommendation}"
            )

    report.append("")

    # ==========================================
    # ISSUE PRIORITIZATION
    # ==========================================

    report.append("ISSUE PRIORITIZATION")
    report.append("------------------------------------------")

    if not prioritized_issues:

        report.append(
            "No significant diagnostic issues identified."
        )

    else:

        report.append("Prioritized Issues")
        report.append("------------------------------------------")

        for issue in prioritized_issues:

            report.append(
                f"{issue['category']} | "
                f"{issue['issue']} | "
                f"Severity: {issue['severity']} | "
                f"Score: {issue['priority_score']}"
            )

        report.append("")

        report.append("Primary Issue")
        report.append("------------------------------------------")

        report.append(
            f"Issue : {primary_issue['issue']}"
        )

        report.append(
            f"Category : {primary_issue['category']}"
        )

        report.append(
            f"Severity : {primary_issue['severity']}"
        )

        report.append(
            f"Priority Score : "
            f"{primary_issue['priority_score']}"
        )

        report.append(
            f"Reason : {primary_issue['reason']}"
        )

    report.append("")

    # ==========================================
    # REPORT FOOTER
    # ==========================================

    report.append("==========================================")
    report.append("END OF WINDOWS TECHNICIAN v0.2 REPORT")
    report.append("==========================================")

    return "\n".join(report)
