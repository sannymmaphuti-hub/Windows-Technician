# ==========================================
# Windows Technician v0.5
# MEMORY COLLECTOR
# ==========================================

import psutil


class MemoryCollector:

    name = "Memory Collector"
    category = "MEMORY"

    def collect(self):

        memory = psutil.virtual_memory()

        return {
            "total_gb": memory.total / (1024 ** 3),
            "used_gb": memory.used / (1024 ** 3),
            "available_gb": memory.available / (1024 ** 3),
            "usage_percent": memory.percent
        }

