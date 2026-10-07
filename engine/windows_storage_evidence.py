# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE EVIDENCE
# ==========================================

from copy import deepcopy


class WindowsStorageEvidence:
    """
    Immutable-style evidence container for Windows storage
    observations.

    This class represents observed storage information only.

    It does NOT:
    - perform storage diagnostics
    - modify storage
    - delete files
    - repair volumes
    - authorize remediation
    - execute remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    def __init__(self, volumes=None):
        if volumes is None:
            volumes = []

        if not isinstance(volumes, list):
            raise ValueError(
                "volumes must be a list."
            )

        self.volumes = deepcopy(volumes)

    @property
    def volume_count(self):
        return len(self.volumes)

    def get_volume(self, drive):
        if not isinstance(drive, str):
            return None

        normalized_drive = drive.strip().upper()

        if not normalized_drive:
            return None

        for volume in self.volumes:
            if not isinstance(volume, dict):
                continue

            volume_drive = volume.get("drive")

            if not isinstance(volume_drive, str):
                continue

            if volume_drive.strip().upper() == normalized_drive:
                return deepcopy(volume)

        return None

    def free_space_ratio(self, drive):
        volume = self.get_volume(drive)

        if volume is None:
            return None

        total_bytes = volume.get("total_bytes")
        free_bytes = volume.get("free_bytes")

        if not isinstance(total_bytes, (int, float)):
            return None

        if not isinstance(free_bytes, (int, float)):
            return None

        if total_bytes <= 0:
            return None

        return free_bytes / total_bytes