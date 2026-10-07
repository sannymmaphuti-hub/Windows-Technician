# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP COLLECTOR
# ==========================================

import json
import subprocess

from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


class WindowsStartupCollector:
    domain = "STARTUP"

    def collect(self):
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-CimInstance Win32_StartupCommand | "
                        "Select-Object Name,Command,Location,User | "
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
            return WindowsStartupEvidence()

        return WindowsStartupEvidence(
            items=self._parse_result(
                result.stdout
            )
        )

    @staticmethod
    def _parse_result(output):
        if not isinstance(output, str):
            return []

        output = output.strip()

        if not output:
            return []

        try:
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

        items = []

        for record in records:
            if not isinstance(record, dict):
                continue

            name = record.get("Name")

            if not isinstance(name, str):
                continue

            name = name.strip()

            if not name:
                continue

            command = record.get(
                "Command"
            )

            location = record.get(
                "Location"
            )

            user = record.get(
                "User"
            )

            items.append(
                {
                    "name": name,
                    "command": (
                        command
                        if isinstance(
                            command,
                            str,
                        )
                        else ""
                    ),
                    "location": (
                        location
                        if isinstance(
                            location,
                            str,
                        )
                        else ""
                    ),
                    "user": (
                        user
                        if isinstance(
                            user,
                            str,
                        )
                        else ""
                    ),
                    "enabled": True,
                }
            )

        return items