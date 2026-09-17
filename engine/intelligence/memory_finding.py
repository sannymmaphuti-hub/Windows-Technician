# ==========================================
# Windows Technician v0.5
# MEMORY FINDING BUILDER
# ==========================================


class MemoryFindingBuilder:

    def build(self, intelligence):

        if intelligence is None:
            raise ValueError(
                "Memory intelligence cannot be None."
            )

        finding = {
            "category": "MEMORY",
            "severity": intelligence.get(
                "severity",
                "INFO"
            ),
            "process": intelligence.get(
                "name",
                "Unknown"
            ),
            "pid": intelligence.get(
                "pid",
                0
            ),
            "is_significant_consumer": intelligence.get(
                "is_significant_consumer",
                False
            ),
            "message": intelligence.get(
                "message",
                ""
            )
        }

        if "confidence" in intelligence:
            finding["confidence"] = (
                intelligence["confidence"]
            )

        return finding

