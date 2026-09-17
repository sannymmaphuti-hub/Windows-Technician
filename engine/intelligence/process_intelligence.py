# ==========================================
# Windows Technician v0.5
# PROCESS INTELLIGENCE
# ==========================================


class ProcessIntelligence:

    CPU_WARNING_THRESHOLD = 80
    CPU_CRITICAL_THRESHOLD = 95

    PERSISTENCE_THRESHOLD = 60

    def analyze(
        self,
        system_cpu_percent,
        process,
        cpu_history=None
    ):
        """
        Analyze a process in the context of
        overall system CPU pressure.
        """

        if process is None:
            return None

        process_name = process.get(
            "name",
            "Unknown"
        )

        process_cpu = process.get(
            "cpu_percent",
            0
        )

        pid = process.get(
            "pid",
            0
        )

        result = {
            "pid": pid,
            "name": process_name,
            "process_cpu_percent": process_cpu,
            "system_cpu_percent": system_cpu_percent,
        }

        # ------------------------------------------
        # Determine CPU pressure
        # ------------------------------------------

        if system_cpu_percent >= self.CPU_CRITICAL_THRESHOLD:

            severity = "CRITICAL"

        elif system_cpu_percent >= self.CPU_WARNING_THRESHOLD:

            severity = "WARNING"

        else:

            severity = "INFO"

        result["severity"] = severity

        # ------------------------------------------
        # Determine process behavior
        # ------------------------------------------
        if cpu_history:

            behavior, persistence_ratio = (
                self._classify_behavior(cpu_history)
            )

            result["behavior"] = behavior
            result["persistence_ratio"] = persistence_ratio

        else:

            result["behavior"] = "UNKNOWN"
            result["persistence_ratio"] = 0.0
        # ------------------------------------------
        # Determine contribution
        # ------------------------------------------

        result["is_significant_contributor"] = (
            system_cpu_percent >= self.CPU_WARNING_THRESHOLD
            and process_cpu >= self.CPU_WARNING_THRESHOLD
        )

        # ------------------------------------------
        # Build diagnostic message
        # ------------------------------------------

        result["message"] = (
            f"{process_name} is using "
            f"{process_cpu:.2f}% CPU while system CPU "
            f"utilization is {system_cpu_percent:.2f}%."
        )

        return result

    def _classify_behavior(self, samples):

        if not samples:
            return "UNKNOWN", 0.0

        high_samples = [
            value
            for value in samples
            if value >= self.CPU_WARNING_THRESHOLD
        ]

        persistence_ratio = (
            len(high_samples)
            / len(samples)
        ) * 100

        if persistence_ratio >= self.PERSISTENCE_THRESHOLD:

            return "PERSISTENT", persistence_ratio

        if high_samples:

            return "SPIKE", persistence_ratio

        return "NORMAL", persistence_ratio

