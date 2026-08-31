# ==========================================
# Windows Technician v0.3
# MEMORY TEMPORAL FINDING BUILDER
# ==========================================


class MemoryTemporalFindingBuilder:

    def build(self, intelligence):

        if intelligence is None:
            raise ValueError(
                "Memory temporal intelligence cannot be None."
            )

        behavior = intelligence.get(
            "behavior",
            "UNKNOWN"
        )

        if behavior == "SPIKE":
            severity = "WARNING"

        elif behavior == "PERSISTENT":
            severity = "WARNING"

        else:
            severity = "INFO"

        process_name = intelligence.get(
            "name",
            "Unknown"
        )

        pid = intelligence.get(
            "pid",
            0
        )

        persistence_ratio = intelligence.get(
            "persistence_ratio",
            0.0
        )

        message = (
            f"{process_name} memory behavior is {behavior}. "
            f"Persistence ratio is "
            f"{persistence_ratio:.2f}."
        )

        return {
            "category": "MEMORY",
            "severity": severity,
            "process": process_name,
            "pid": pid,
            "behavior": behavior,
            "persistence_ratio": persistence_ratio,
            "is_sustained_consumer": intelligence.get(
                "is_sustained_consumer",
                False
            ),
            "message": message
        }
