import platform
import socket

from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)


class WindowsSystemCollector:
    domain = "SYSTEM"

    def collect(self):
        try:
            return WindowsSystemEvidence(
                computer_name=self._safe_string(
                    socket.gethostname()
                ),
                operating_system=self._safe_string(
                    platform.system()
                ),
                os_version=self._safe_string(
                    platform.version()
                ),
                architecture=self._safe_string(
                    platform.machine()
                ),
                processor=self._safe_string(
                    platform.processor()
                ),
            )
        except (OSError, ValueError):
            return WindowsSystemEvidence()

    @staticmethod
    def _safe_string(value):
        if not isinstance(value, str):
            return ""

        return value.strip()