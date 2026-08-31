# ==========================================
# Windows Technician v0.3
# PROCESS COLLECTOR
# ==========================================

from diagnostics.process_analyzer import (
    get_process_snapshot,
    get_process_cpu_history,
)


class ProcessCollector:

    category = "PROCESS"

    def collect(self):

        processes = get_process_snapshot()

        return {
            "processes": processes
        }

    def collect_cpu_history(
        self,
        sample_count=5,
        interval=1
    ):

        return get_process_cpu_history(
            sample_count=sample_count,
            interval=interval
        )
