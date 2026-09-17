# ==========================================
# Windows Technician v0.5
# MEMORY INTELLIGENCE
# ==========================================


class MemoryIntelligence:

    MEMORY_WARNING_THRESHOLD = 80
    MEMORY_CRITICAL_THRESHOLD = 90

    PROCESS_MEMORY_SIGNIFICANT_THRESHOLD = 1000

    def analyze(
        self,
        system_memory_percent,
        process
    ):
        """
        Analyze a process in the context of
        overall system memory pressure.
        """

        if process is None:
            return None

        process_name = process.get(
            "name",
            "Unknown"
        )

        process_memory = process.get(
            "memory_mb",
            0
        )

        pid = process.get(
            "pid",
            0
        )

        result = {
            "pid": pid,
            "name": process_name,
            "process_memory_mb": process_memory,
            "system_memory_percent": system_memory_percent,
        }

        # ------------------------------------------
        # Determine memory pressure
        # ------------------------------------------

        if system_memory_percent >= self.MEMORY_CRITICAL_THRESHOLD:

            severity = "CRITICAL"

        elif system_memory_percent >= self.MEMORY_WARNING_THRESHOLD:

            severity = "WARNING"

        else:

            severity = "INFO"

        result["severity"] = severity

        # ------------------------------------------
        # Determine significant memory consumer
        # ------------------------------------------

        result["is_significant_consumer"] = (
            system_memory_percent >= self.MEMORY_WARNING_THRESHOLD
            and process_memory >= self.PROCESS_MEMORY_SIGNIFICANT_THRESHOLD
        )

        # ------------------------------------------
        # Build diagnostic message
        # ------------------------------------------

        result["message"] = (
            f"{process_name} is using "
            f"{process_memory:.2f} MB memory while system memory "
            f"utilization is {system_memory_percent:.2f}%."
        )

        return result

