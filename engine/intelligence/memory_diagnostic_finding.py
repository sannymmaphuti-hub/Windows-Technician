# ==========================================
# Windows Technician v0.6
# MEMORY DIAGNOSTIC FINDING BUILDER
# ==========================================


class MemoryDiagnosticFindingBuilder:

    def build(self, intelligence):

        if intelligence is None:
            raise ValueError(
                "Memory diagnostic intelligence cannot be None."
            )

        process_name = intelligence.get(
            "name",
            "Unknown"
        )

        pid = intelligence.get(
            "pid",
            0
        )

        severity = intelligence.get(
            "severity",
            "INFO"
        )

        process_memory_mb = intelligence.get(
            "process_memory_mb",
            0
        )

        system_memory_percent = intelligence.get(
            "system_memory_percent",
            0.0
        )

        behavior = intelligence.get(
            "behavior",
            "UNKNOWN"
        )

        persistence_ratio = intelligence.get(
            "persistence_ratio",
            0.0
        )

        trend = intelligence.get(
            "trend",
            "UNKNOWN"
        )

        change_percent = intelligence.get(
            "change_percent",
            0.0
        )

        message = intelligence.get(
            "message",
            ""
        )

        # Reuse established thresholds: system memory >= 80%
        # and process memory >= 1000 MB.
        try:
            system_usage = float(system_memory_percent)
            process_usage = float(process_memory_mb)
        except (TypeError, ValueError):
            system_usage = 0.0
            process_usage = 0.0

        finding = {
            "category": "MEMORY",
            "severity": severity,
            "process": process_name,
            "pid": pid,
            "process_memory_mb": process_memory_mb,
            "system_memory_percent": system_memory_percent,
            "behavior": behavior,
            "persistence_ratio": persistence_ratio,
            "trend": trend,
            "change_percent": change_percent,
            "message": message
        }

        if system_usage >= 80 and process_usage >= 1000:
            finding["finding_type"] = "HIGH_PROCESS_MEMORY"

        return finding
