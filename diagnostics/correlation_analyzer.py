# ==========================================================
# WINDOWS TECHNICIAN v0.1
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
    """

    findings = []

    memory_status = memory_diagnostics["status"]

    # ======================================================
    # MEMORY PRESSURE + CPU BEHAVIOR
    # ======================================================

    if memory_status in (
        "WARNING",
        "HIGH MEMORY PRESSURE"
    ):

        for finding in process_behavior_findings:

            process_name = finding["name"]
            classification = finding["classification"]

            if (
                process_name.lower() == "memcompression"
                and classification == "CPU SPIKE"
            ):

                findings.append({
                    "severity": "INFO",
                    "category": "CROSS-DIAGNOSTIC CORRELATION",
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
        "status": "HIGH MEMORY PRESSURE"
    }

    test_behavior = [
        {
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "name": "MemCompression",
            "classification": "CPU SPIKE",
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