# ==========================================
# Windows Technician v0.3
# PROCESS INTELLIGENCE PIPELINE
# ==========================================


from engine.intelligence.process_intelligence import (
    ProcessIntelligence
)

from engine.intelligence.process_finding import (
    ProcessFindingBuilder
)


class ProcessIntelligencePipeline:

    def __init__(
        self,
        intelligence=None,
        finding_builder=None
    ):

        self.intelligence = (
            intelligence
            or ProcessIntelligence()
        )

        self.finding_builder = (
            finding_builder
            or ProcessFindingBuilder()
        )

    def analyze(
        self,
        cpu_evidence,
        process_evidence,
        process_cpu_history=None
    ):

        if not cpu_evidence:
            return {
                "intelligence": None,
                "finding": None
            }

        if not process_evidence:
            return {
                "intelligence": None,
                "finding": None
            }

        system_cpu = cpu_evidence.get(
            "usage_percent"
        )

        processes = process_evidence.get(
            "processes",
            []
        )

        if system_cpu is None:
            return {
                "intelligence": None,
                "finding": None
            }

        if not processes:
            return {
                "intelligence": None,
                "finding": None
            }

        # ------------------------------------------
        # Identify top CPU process
        # ------------------------------------------

        top_process = max(
            processes,
            key=lambda process: process.get(
                "cpu_percent",
                0
            )
        )

        # ------------------------------------------
        # Find historical samples
        # ------------------------------------------

        history_samples = []

        for history_entry in (
            process_cpu_history or []
        ):

            if (
                history_entry.get("pid")
                == top_process.get("pid")
            ):

                history_samples = (
                    history_entry.get(
                        "samples",
                        []
                    )
                )

                break

        # ------------------------------------------
        # Process intelligence
        # ------------------------------------------

        intelligence = (
            self.intelligence.analyze(
                system_cpu_percent=system_cpu,
                process=top_process,
                cpu_history=history_samples
            )
        )

        if intelligence is None:

            return {
                "intelligence": None,
                "finding": None
            }

        # ------------------------------------------
        # Process finding
        # ------------------------------------------

        finding = (
            self.finding_builder.build(
                intelligence
            )
        )

        return {
            "intelligence": intelligence,
            "finding": finding
        }
