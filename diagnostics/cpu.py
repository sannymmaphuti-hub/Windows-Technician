import psutil


def get_cpu_info():
    usage = psutil.cpu_percent(interval=1)

    if usage > 95:
        status = "VERY HIGH"
    elif usage >= 80:
        status = "HIGH"
    else:
        status = "NORMAL"

    cpu_info = {
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True),
        "usage_percent": usage,
        "frequency_mhz": psutil.cpu_freq().current,
        "status": status
    }

    return cpu_info

def analyze_cpu(cpu_info):

    usage = cpu_info["usage_percent"]

    if usage < 70:
        status = "HEALTHY"
        severity = "INFO"
        finding = "CPU utilization is within a normal operating range."
        recommendation = "No immediate CPU action is required."

    elif usage < 80:
        status = "ATTENTION"
        severity = "INFO"
        finding = "CPU utilization is moderately elevated."
        recommendation = "Monitor CPU usage and identify applications causing sustained load."

    elif usage < 95:
        status = "WARNING"
        severity = "WARNING"
        finding = "CPU utilization is high."
        recommendation = "Investigate the highest CPU-consuming processes and determine whether the load is expected."

    else:
        status = "CRITICAL"
        severity = "CRITICAL"
        finding = "CPU utilization is extremely high."
        recommendation = "Investigate high CPU-consuming processes immediately and determine the cause of sustained processor load."

    return {
        "status": status,
        "severity": severity,
        "finding": finding,
        "recommendation": recommendation
    }

def analyze_cpu_contributors(top_processes):

    if not top_processes:
        return {
            "process": None,
            "cpu_percent": 0,
            "finding": "No CPU process data is available."
        }

    top_process = top_processes[0]

    return {
        "process": top_process["name"],
        "cpu_percent": top_process["cpu_percent"],
        "finding": (
            f"{top_process['name']} is currently the highest "
            f"CPU-consuming process at "
            f"{top_process['cpu_percent']:.2f}%."
        )
    }

def generate_cpu_diagnostics(cpu_info, top_processes):

    cpu_diagnosis = analyze_cpu(cpu_info)
    contributor = analyze_cpu_contributors(top_processes)

    findings = []

    findings.append({
        "severity": cpu_diagnosis["severity"],
        "category": "CPU",
        "message": cpu_diagnosis["finding"]
    })

    if contributor["process"] is not None:

        if cpu_info["usage_percent"] >= 95:
            contributor_severity = "CRITICAL"

        elif cpu_info["usage_percent"] >= 80:
            contributor_severity = "WARNING"

        else:
            contributor_severity = "INFO"

        if cpu_info["usage_percent"] >= 80:

            message = contributor["finding"]

        else:

            message = (
                f"{contributor['process']} is currently the highest "
                f"CPU consumer, but overall CPU utilization is "
                f"within a normal range."
            )

        findings.append({
            "severity": contributor_severity,
            "category": "CPU CONTRIBUTOR",
            "message": message
        })

    return {
        "status": cpu_diagnosis["status"],
        "findings": findings,
        "recommendation": cpu_diagnosis["recommendation"]
    }
def get_top_cpu_processes(limit=5):
    processes = []

    for process in psutil.process_iter(["pid", "name"]):
        try:
            # Ignore the Windows System Idle Process
            if process.pid == 0:
                continue

            process.cpu_percent(None)
            processes.append(process)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    import time
    time.sleep(1)

    results = []

    logical_cpus = psutil.cpu_count(logical=True)

    for process in processes:
        try:
            cpu_usage = process.cpu_percent(None)

            # Convert process CPU usage to percentage
            # of the entire machine.
            normalized_usage = cpu_usage / logical_cpus

            results.append({
                "pid": process.pid,
                "name": process.name(),
                "cpu_percent": normalized_usage
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    results.sort(
        key=lambda process: process["cpu_percent"],
        reverse=True
    )

    return results[:limit]

