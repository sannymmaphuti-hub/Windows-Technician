# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE COLLECTOR
# ==========================================

import os
import shutil

from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)


class WindowsStorageCollector:
    """
    Read-only collector for Windows storage information.

    The collector gathers basic filesystem information for
    available Windows drives.

    It does NOT:
    - modify storage
    - delete files
    - format volumes
    - repair volumes
    - authorize remediation
    - execute remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "STORAGE"

    def collect(self):
        """
        Collect basic storage information.

        Each discovered drive produces a volume dictionary
        containing its drive identifier, total capacity,
        and available free space.
        """

        volumes = []

        for drive in self._available_drives():
            try:
                total_bytes, free_bytes = (
                    self._disk_usage(drive)
                )
            except OSError:
                continue

            volumes.append(
                {
                    "drive": drive,
                    "total_bytes": total_bytes,
                    "free_bytes": free_bytes,
                }
            )

        return WindowsStorageEvidence(
            volumes=volumes
        )

    @staticmethod
    def _available_drives():
        """
        Return available filesystem drives.

        On Windows, os.listdrives() provides mounted
        drive roots.

        A fallback is provided for environments where
        os.listdrives() is unavailable.
        """

        listdrives = getattr(
            os,
            "listdrives",
            None,
        )

        if callable(listdrives):
            return listdrives()

        return ["C:\\"]

    @staticmethod
    def _disk_usage(drive):
        """
        Return total and free bytes for a drive.
        """

        usage = shutil.disk_usage(drive)

        return (
            usage.total,
            usage.free,
        )