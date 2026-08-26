# ==========================================
# WINDOWS TECHNICIAN v0.1
# CPU EVIDENCE COLLECTOR
# ==========================================

from diagnostics.cpu import get_cpu_info, get_top_cpu_processes


class CPUCollector:

    category = "CPU"

    def collect(self):

        cpu_info = get_cpu_info()

        top_processes = get_top_cpu_processes()

        return {
            "physical_cores": cpu_info["physical_cores"],
            "logical_processors": cpu_info["logical_processors"],
            "usage_percent": cpu_info["usage_percent"],
            "frequency_mhz": cpu_info["frequency_mhz"],
            "status": cpu_info["status"],
            "top_processes": top_processes
        }