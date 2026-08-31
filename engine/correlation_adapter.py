# ==========================================
# Windows Technician v0.3
# CORRELATION ADAPTER
# ==========================================


def build_process_cpu_behavior_findings(
    process_intelligence
):
    """
    Adapt ProcessIntelligence output into the
    structure expected by the correlation engine.

    This preserves the contracts of the existing
    intelligence and finding layers.
    """

    if process_intelligence is None:
        return []

    behavior = process_intelligence.get(
        "behavior",
        "UNKNOWN"
    )

    if behavior not in (
        "SPIKE",
        "PERSISTENT"
    ):
        return []

    return [
        {
            "name": process_intelligence.get(
                "name",
                "Unknown"
            ),

            "pid": process_intelligence.get(
                "pid",
                0
            ),

            "severity": process_intelligence.get(
                "severity",
                "INFO"
            ),

            "category": "PROCESS CPU BEHAVIOR",

            "classification": (
                f"CPU {behavior}"
            ),

            "message": process_intelligence.get(
                "message",
                ""
            )
        }
    ]
