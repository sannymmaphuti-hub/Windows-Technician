
# ==========================================
# Windows Technician v0.6
# GPU DIAGNOSTICS
# ==========================================

import subprocess


def get_gpu_info():
    """
    Collect basic GPU information from Windows.
    """

    gpu_info = []

    try:
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name, AdapterRAM, DriverVersion, Status | "
            "ConvertTo-Json"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode != 0:
            return [{
                "name": "Unknown",
                "memory": 0,
                "driver": "Unknown",
                "status": "UNKNOWN"
            }]

        import json

        data = json.loads(result.stdout)

        # Windows returns a dictionary when only one GPU exists
        if isinstance(data, dict):
            data = [data]

        for gpu in data:
            adapter_ram = gpu.get("AdapterRAM")

            if adapter_ram:
                memory_gb = round(adapter_ram / (1024 ** 3), 2)
            else:
                memory_gb = 0

            gpu_info.append({
                "name": gpu.get("Name", "Unknown"),
                "memory": memory_gb,
                "driver": gpu.get("DriverVersion", "Unknown"),
                "status": gpu.get("Status", "Unknown")
            })

    except Exception as error:
        gpu_info.append({
            "name": "Unknown",
            "memory": 0,
            "driver": "Unknown",
            "status": f"ERROR: {error}"
        })

    return gpu_info


def diagnose_gpu(gpu_info):
    """
    Analyze GPU information and produce diagnostic findings.
    """

    findings = []
    recommendations = []

    if not gpu_info:
        findings.append(
            "[WARNING] GPU : No GPU information could be detected."
        )

        recommendations.append(
            "Check whether the graphics adapter is properly detected."
        )

        return findings, recommendations

    for gpu in gpu_info:

        name = gpu["name"]
        status = str(gpu["status"]).lower()

        if status == "ok":
            findings.append(
                f"[INFO] GPU : {name} is detected and reports a healthy status."
            )

        elif status == "unknown":
            findings.append(
                f"[WARNING] GPU : {name} status could not be determined."
            )

            recommendations.append(
                f"Investigate the device status for {name}."
            )

        else:
            findings.append(
                f"[WARNING] GPU : {name} reports status '{gpu['status']}'."
            )

            recommendations.append(
                f"Investigate the GPU device status for {name}."
            )

    return findings, recommendations
