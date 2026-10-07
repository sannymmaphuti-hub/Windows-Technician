# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES COLLECTOR
# ==========================================

import subprocess

from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


class WindowsServicesCollector:
    """
    Read-only collector for Windows service information.

    The collector gathers service name, display name,
    current status, and startup type.

    It does NOT:
    - start services
    - stop services
    - enable services
    - disable services
    - modify Windows configuration
    - authorize remediation
    - execute remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "SERVICES"

    def collect(self):
        """
        Collect Windows service information.

        PowerShell is used because it provides a stable
        Windows-native service query interface.
        """

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-CimInstance Win32_Service | "
                        "Select-Object Name,DisplayName,"
                        "State,StartMode | "
                        "ConvertTo-Json -Compress"
                    ),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        except (
            OSError,
            subprocess.SubprocessError,
        ):
            return WindowsServicesEvidence()

        services = self._parse_result(
            result.stdout
        )

        return WindowsServicesEvidence(
            services=services
        )

    @staticmethod
    def _parse_result(output):
        if not isinstance(output, str):
            return []

        output = output.strip()

        if not output:
            return []

        try:
            import json

            records = json.loads(output)
        except (
            ValueError,
            TypeError,
        ):
            return []

        if isinstance(records, dict):
            records = [records]

        if not isinstance(records, list):
            return []

        services = []

        for record in records:
            if not isinstance(record, dict):
                continue

            name = record.get("Name")
            display_name = record.get("DisplayName")
            state = record.get("State")
            start_mode = record.get("StartMode")

            if not isinstance(name, str):
                continue

            services.append(
                {
                    "name": name,
                    "display_name": (
                        display_name
                        if isinstance(
                            display_name,
                            str,
                        )
                        else name
                    ),
                    "status": (
                        WindowsServicesCollector
                        ._normalize_status(state)
                    ),
                    "start_type": (
                        WindowsServicesCollector
                        ._normalize_start_type(
                            start_mode
                        )
                    ),
                }
            )

        return services

    @staticmethod
    def _normalize_status(status):
        if not isinstance(status, str):
            return "UNKNOWN"

        normalized = status.strip().upper()

        if normalized == "RUNNING":
            return "RUNNING"

        if normalized == "STOPPED":
            return "STOPPED"

        return "UNKNOWN"

    @staticmethod
    def _normalize_start_type(start_type):
        if not isinstance(start_type, str):
            return "UNKNOWN"

        normalized = start_type.strip().upper()

        mapping = {
            "AUTO": "AUTO",
            "AUTOMATIC": "AUTO",
            "MANUAL": "MANUAL",
            "DISABLED": "DISABLED",
        }

        return mapping.get(
            normalized,
            "UNKNOWN",
        )