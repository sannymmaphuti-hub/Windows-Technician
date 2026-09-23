# ==========================================
# Windows Technician v0.6
# STORAGE COLLECTOR
# ==========================================

import psutil


class StorageCollector:

    name = "Storage Collector"
    category = "STORAGE"

    def collect(self):

        storage_devices = []

        for partition in psutil.disk_partitions():

            try:

                usage = psutil.disk_usage(
                    partition.mountpoint
                )

                storage_devices.append({

                    "device": partition.device,

                    "mountpoint": partition.mountpoint,

                    "filesystem": partition.fstype,

                    "total_gb": usage.total / (1024 ** 3),

                    "used_gb": usage.used / (1024 ** 3),

                    "free_gb": usage.free / (1024 ** 3),

                    "usage_percent": usage.percent,

                    "free_percent": 100 - usage.percent
                })

            except (
                PermissionError,
                OSError
            ):

                continue

        return storage_devices
