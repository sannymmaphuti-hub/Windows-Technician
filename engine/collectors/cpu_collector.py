# ==========================================
# Windows Technician v0.5
# CPU EVIDENCE COLLECTOR
# ==========================================

from concurrent.futures import ThreadPoolExecutor

from diagnostics.cpu import (
    get_cpu_info,
    get_top_cpu_processes,
)


class CPUCollector:

    category = "CPU"

    def collect(self):

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:

            cpu_info_future = executor.submit(
                get_cpu_info
            )

            top_processes_future = executor.submit(
                get_top_cpu_processes
            )

            cpu_info = cpu_info_future.result()

            top_processes = (
                top_processes_future.result()
            )

        return {
            "physical_cores": cpu_info["physical_cores"],
            "logical_processors": cpu_info["logical_processors"],
            "usage_percent": cpu_info["usage_percent"],
            "frequency_mhz": cpu_info["frequency_mhz"],
            "status": cpu_info["status"],
            "top_processes": top_processes
        }
