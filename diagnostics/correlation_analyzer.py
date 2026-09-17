# ==========================================================
# Windows Technician v0.5
# DIAGNOSTIC CORRELATION ENGINE
# ==========================================================


def correlate_memory_and_cpu_behavior(
    memory_diagnostics,
    process_behavior_findings
):
    """
    Correlate memory pressure with CPU behaviour.

    This function does not claim causation.
    It identifies evidence that may indicate
    a relationship between memory pressure
    and CPU behaviour.

    Supports both:
        - Legacy correlation findings using
          "classification": "CPU SPIKE"
        - process intelligence findings using
          "behavior": "SPIKE"
    """

    findings = []

    if not isinstance(memory_diagnostics, dict):
        return findings

    if not isinstance(process_behavior_findings, list):
        return findings

    memory_status = memory_diagnostics.get(
        "status",
        "INFO"
    )

    # ======================================================
    # MEMORY PRESSURE
    # ======================================================

    if memory_status not in (
        "WARNING",
        "CRITICAL",
        "HIGH MEMORY PRESSURE"
    ):
        return findings

    # ======================================================
    # PROCESS BEHAVIOR
    # ======================================================

    for finding in process_behavior_findings:

        if not isinstance(finding, dict):
            continue

        process_name = finding.get(
            "name",
            "Unknown"
        )

        # --------------------------------------------------
        # Support both old and new field names.
        # --------------------------------------------------

        behavior = finding.get(
            "behavior"
        )

        classification = finding.get(
            "classification"
        )

        is_cpu_spike = (
            behavior == "SPIKE"
            or classification == "CPU SPIKE"
        )

        # --------------------------------------------------
        # MemCompression + CPU spike
        # --------------------------------------------------

        if (
            isinstance(process_name, str)
            and process_name.lower() == "memcompression"
            and is_cpu_spike
        ):

            findings.append({
                "severity": "INFO",
                "category": (
                    "CROSS-DIAGNOSTIC CORRELATION"
                ),
                "relationship": (
                    "MEMORY PRESSURE + CPU SPIKE"
                ),
                "process": process_name,
                "message": (
                    "High memory pressure coincided "
                    "with temporary CPU activity from "
                    "MemCompression. This may indicate "
                    "Windows responding to memory pressure."
                )
            })

    return findings


# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    test_memory = {
        "status": "CRITICAL"
    }

    test_behavior = [
        {
            "severity": "CRITICAL",
            "category": "PROCESS CPU BEHAVIOR",
            "name": "MemCompression",
            "behavior": "SPIKE",
            "message": (
                "MemCompression experienced "
                "temporary high CPU activity."
            )
        }
    ]

    result = correlate_memory_and_cpu_behavior(
        test_memory,
        test_behavior
    )

    print("==========================================")
    print("CORRELATION ENGINE TEST")
    print("==========================================")

    if not result:

        print()
        print("No cross-diagnostic relationships detected.")

    else:

        print()

        for finding in result:

            print(
                f"[{finding['severity']}] "
                f"{finding['category']}"
            )

            print(
                f"Relationship : "
                f"{finding['relationship']}"
            )

            print(
                f"Process : "
                f"{finding['process']}"
            )

            print(
                f"Message : "
                f"{finding['message']}"
            )

