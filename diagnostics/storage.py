import psutil


def get_storage_info():
    storage = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            storage.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype,
                "total_gb": usage.total / (1024 ** 3),
                "used_gb": usage.used / (1024 ** 3),
                "free_gb": usage.free / (1024 ** 3),
                "usage_percent": usage.percent
            })

        except (PermissionError, OSError):
            continue

    return storage

def analyze_storage(usage_percent):

    if usage_percent < 80:
        status = "HEALTHY"
        diagnosis = "Storage capacity is healthy."
        recommendation = "No immediate storage action is required."

    elif usage_percent < 90:
        status = "ATTENTION"
        diagnosis = "Storage usage is becoming high."
        recommendation = "Review large files and consider freeing unused space."

    elif usage_percent < 95:
        status = "WARNING"
        diagnosis = "Storage usage is very high."
        recommendation = "Free disk space soon by removing unnecessary files."

    else:
        status = "CRITICAL"
        diagnosis = "Storage capacity is critically low."
        recommendation = "Free disk space immediately to prevent system and application problems."

    return {
        "status": status,
        "diagnosis": diagnosis,
        "recommendation": recommendation
    }

def generate_storage_diagnostics(storage_data):

    diagnostics = []

    for drive in storage_data:
        result = analyze_storage(drive["usage_percent"])

        if result["status"] == "HEALTHY":
            severity = "INFO"

        elif result["status"] == "ATTENTION":
            severity = "INFO"

        elif result["status"] == "WARNING":
            severity = "WARNING"

        else:
            severity = "CRITICAL"

        diagnostics.append({
            "drive": drive["mountpoint"],
            "usage_percent": drive["usage_percent"],
            "status": result["status"],
            "severity": severity,
            "finding": result["diagnosis"],
            "recommendation": result["recommendation"]
        })

    return diagnostics
