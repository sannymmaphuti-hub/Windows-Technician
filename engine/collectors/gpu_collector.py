import json
import subprocess


class GPUCollector:
    name = "GPU Collector"
    category = "GPU"


    def collect(self):

        command = (
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name, AdapterRAM, DriverVersion, Status | "
            "ConvertTo-Json -Compress"
        )

        try:

            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    command
                ],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            output = result.stdout.strip()

            if not output:
                return []

            data = json.loads(output)

            if isinstance(data, dict):
                data = [data]

            gpus = []

            for gpu in data:

                adapter_ram = gpu.get("AdapterRAM")

                if isinstance(adapter_ram, (int, float)):
                    memory_gb = adapter_ram / (1024 ** 3)
                else:
                    memory_gb = 0

                gpus.append({
                    "name": gpu.get("Name"),
                    "memory_gb": memory_gb,
                    "driver_version": gpu.get("DriverVersion"),
                    "status": gpu.get("Status")
                })

            return gpus

        except (
            subprocess.SubprocessError,
            subprocess.TimeoutExpired,
            json.JSONDecodeError,
            OSError
        ):

            return []

