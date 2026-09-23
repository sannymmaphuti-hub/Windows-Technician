
def analyze_memory_consumers(memory_by_application):
    consumers = sorted(
        memory_by_application,
        key=lambda app: app["memory_mb"],
        reverse=True
    )

    return consumers[:3]

def analyze_resource_correlation(
    memory_info,
    top_memory_consumers,
    top_cpu_processes
):
    findings = []

    memory_usage = memory_info["usage_percent"]
    available_gb = memory_info["available_gb"]

    # --------------------------------------------------
    # MEMORY CORRELATION
    # --------------------------------------------------

    if memory_usage >= 95:

        findings.append({
            "severity": "CRITICAL",
            "category": "MEMORY",
            "message": (
                f"System memory usage is {memory_usage:.1f}%, "
                "indicating critical memory pressure."
            )
        })

    elif memory_usage >= 90 or available_gb <= 0.50:

        findings.append({
            "severity": "WARNING",
            "category": "MEMORY",
            "message": (
                f"System memory usage is {memory_usage:.1f}%, "
                "indicating high memory pressure."
            )
        })

    elif memory_usage >= 80:

        findings.append({
            "severity": "WARNING",
            "category": "MEMORY",
            "message": (
                f"System memory usage is {memory_usage:.1f}%, "
                "indicating elevated memory utilization."
            )
        })

    elif memory_usage >= 70:

        findings.append({
            "severity": "INFO",
            "category": "MEMORY",
            "message": (
                f"System memory usage is {memory_usage:.1f}%, "
                "which is moderately elevated."
            )
        })

    # --------------------------------------------------
    # MEMORY CONTRIBUTOR
    # --------------------------------------------------

    if top_memory_consumers:

        largest_memory_consumer = top_memory_consumers[0]

        findings.append({
            "severity": "INFO",
            "category": "MEMORY CONTRIBUTOR",
            "message": (
                f"{largest_memory_consumer['name']} is the "
                f"largest grouped memory consumer at "
                f"{largest_memory_consumer['memory_mb']:.2f} MB."
            )
        })

    # --------------------------------------------------
    # CPU CONTRIBUTOR
    # --------------------------------------------------

    if top_cpu_processes:

        largest_cpu_process = top_cpu_processes[0]

        findings.append({
            "severity": "INFO",
            "category": "CPU CONTRIBUTOR",
            "message": (
                f"{largest_cpu_process['name']} is currently "
                f"the highest CPU consumer."
            )
        })

    return findings

def identify_root_cause_candidates(
    memory_info,
    top_memory_consumers,
    top_cpu_processes
):
    candidates = []

    memory_usage = memory_info["usage_percent"]
    available_gb = memory_info["available_gb"]
    total_gb = memory_info["total_gb"]

    # ==================================================
    # MEMORY PRESSURE ANALYSIS
    # ==================================================

    if memory_usage >= 95 or available_gb <= 0.25:

        memory_pressure = "CRITICAL"

    elif memory_usage >= 85 or available_gb <= 0.50:

        memory_pressure = "HIGH"

    elif memory_usage >= 80:

        memory_pressure = "ELEVATED"

    else:

        memory_pressure = "NORMAL"

    # ==================================================
    # MEMORY ROOT-CAUSE ANALYSIS
    # ==================================================

    if memory_pressure in ["CRITICAL", "HIGH"]:

        evidence = []

        evidence.append(
            f"Total physical RAM is {total_gb:.2f} GB"
        )

        evidence.append(
            f"RAM usage is {memory_usage:.1f}%"
        )

        evidence.append(
            f"Available RAM is {available_gb:.2f} GB"
        )

        # --------------------------------------------------
        # Determine whether one application dominates usage
        # --------------------------------------------------

        if top_memory_consumers:

            largest = top_memory_consumers[0]

            largest_memory = largest["memory_mb"]

            total_memory_mb = total_gb * 1024

            memory_share = (
                largest_memory / total_memory_mb
            ) * 100

            evidence.append(
                f"{largest['name']} uses "
                f"{largest_memory:.2f} MB"
            )

            evidence.append(
                f"{largest['name']} accounts for approximately "
                f"{memory_share:.1f}% of physical RAM"
            )

            # --------------------------------------------------
            # Strong single-application contributor
            # --------------------------------------------------

            if memory_share >= 30:

                candidates.append({
                    "problem": "High memory pressure",
                    "likely_source": largest["name"],
                    "confidence": 70,
                    "evidence": evidence + [
                        (
                            f"{largest['name']} is consuming a "
                            "significant portion of available "
                            "physical memory."
                        )
                    ],
                    "recommendation": (
                        f"Investigate {largest['name']} and determine "
                        "whether its memory consumption is expected. "
                        "Close unnecessary instances or applications "
                        "if memory pressure continues."
                    )
                })

            # --------------------------------------------------
            # Multiple applications contributing
            # --------------------------------------------------

            else:

                candidates.append({
                    "problem": "High memory pressure",
                    "likely_source": "Multiple applications",
                    "confidence": 80,
                    "evidence": evidence + [
                        (
                            "No single application currently accounts "
                            "for a dominant portion of physical memory."
                        ),
                        (
                            "Memory pressure appears to result from "
                            "combined application and system usage."
                        )
                    ],
                    "recommendation": (
                        "Close unnecessary applications and monitor "
                        "memory usage. If high memory pressure occurs "
                        "regularly, consider increasing physical RAM."
                    )
                })

    # ==================================================
    # ELEVATED MEMORY
    # ==================================================

    elif memory_pressure == "ELEVATED":

        candidates.append({
            "problem": "Elevated memory utilization",
            "likely_source": "Multiple applications",
            "confidence": 40,
            "evidence": [
                f"Total physical RAM is {total_gb:.2f} GB",
                f"RAM usage is {memory_usage:.1f}%",
                f"Available RAM is {available_gb:.2f} GB",
                (
                    "Memory usage is elevated but has not reached "
                    "critical pressure."
                )
            ],
            "recommendation": (
                "Monitor memory usage during normal workloads "
                "and identify whether the condition persists."
            )
        })

    # ==================================================
    # CPU ANALYSIS
    # ==================================================

    if top_cpu_processes:

        largest_cpu = top_cpu_processes[0]

        cpu_usage = largest_cpu["cpu_percent"]

        if cpu_usage >= 80:

            candidates.append({
                "problem": "Severe CPU activity",
                "likely_source": largest_cpu["name"],
                "confidence": 85,
                "evidence": [
                    (
                        f"{largest_cpu['name']} is using "
                        f"{cpu_usage:.1f}% CPU"
                    ),
                    (
                        "CPU activity is high enough to potentially "
                        "affect system responsiveness."
                    )
                ],
                "recommendation": (
                    f"Investigate {largest_cpu['name']} and determine "
                    "whether the CPU activity is expected."
                )
            })

        elif cpu_usage >= 50:

            candidates.append({
                "problem": "High CPU activity",
                "likely_source": largest_cpu["name"],
                "confidence": 65,
                "evidence": [
                    (
                        f"{largest_cpu['name']} is using "
                        f"{cpu_usage:.1f}% CPU"
                    )
                ],
                "recommendation": (
                    f"Monitor {largest_cpu['name']} and determine "
                    "whether the CPU activity is expected."
                )
            })

    return candidates
