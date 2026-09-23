# ==========================================
# Windows Technician v0.6
# MEMORY DIAGNOSTIC INTELLIGENCE
# ==========================================


class MemoryDiagnosticIntelligence:

    CRITICAL_MEMORY_THRESHOLD = 90
    WARNING_MEMORY_THRESHOLD = 80

    def analyze(
        self,
        system_memory_percent,
        temporal_intelligence,
        trend_intelligence
    ):

        if temporal_intelligence is None:
            return None

        process_name = temporal_intelligence.get(
            "name",
            "Unknown"
        )

        pid = temporal_intelligence.get(
            "pid",
            0
        )

        process_memory = temporal_intelligence.get(
            "process_memory_mb",
            0
        )

        behavior = temporal_intelligence.get(
            "behavior",
            "UNKNOWN"
        )

        is_sustained_consumer = temporal_intelligence.get(
            "is_sustained_consumer",
            False
        )

        persistence_ratio = temporal_intelligence.get(
            "persistence_ratio",
            0.0
        )

        trend = {}

        if trend_intelligence is not None:
            trend = trend_intelligence

        trend_direction = trend.get(
            "trend",
            "UNKNOWN"
        )

        change_percent = trend.get(
            "change_percent",
            0.0
        )

        is_significant_rise = trend.get(
            "is_significant_rise",
            False
        )

        # ------------------------------------------
        # Determine diagnostic severity
        # ------------------------------------------

        if (
            system_memory_percent >=
            self.CRITICAL_MEMORY_THRESHOLD
            and is_sustained_consumer
            and trend_direction == "RISING"
        ):

            severity = "CRITICAL"

            message = (
                f"Critical memory pressure detected. "
                f"{process_name} (PID {pid}) is a sustained "
                f"memory consumer while system memory usage "
                f"is {system_memory_percent:.1f}% and trending "
                f"upward by {change_percent:.1f}%."
            )

        elif (
            system_memory_percent >=
            self.WARNING_MEMORY_THRESHOLD
            and (
                is_sustained_consumer
                or is_significant_rise
            )
        ):

            severity = "WARNING"

            message = (
                f"Elevated memory pressure detected. "
                f"{process_name} (PID {pid}) is associated "
                f"with sustained or increasing memory usage."
            )

        else:

            severity = "INFO"

            message = (
                f"Memory usage is currently stable. "
                f"{process_name} (PID {pid}) does not show "
                f"significant sustained memory pressure."
            )

        return {
            "severity": severity,
            "name": process_name,
            "pid": pid,
            "process_memory_mb": process_memory,
            "system_memory_percent": system_memory_percent,
            "behavior": behavior,
            "persistence_ratio": persistence_ratio,
            "trend": trend_direction,
            "change_percent": change_percent,
            "is_significant_rise": is_significant_rise,
            "message": message
        }
