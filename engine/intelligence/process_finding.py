# ==========================================
# WINDOWS TECHNICIAN v0.2
# PROCESS FINDING BUILDER
# ==========================================


class ProcessFindingBuilder:

    def build(self, intelligence):

        if intelligence is None:
            raise ValueError(
                "Process intelligence cannot be None."
            )

        finding = {
            "category": "PROCESS",
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
            "behavior": intelligence.get(
                "behavior",
                "UNKNOWN"
            ),
            "is_significant_contributor": intelligence.get(
                "is_significant_contributor",
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