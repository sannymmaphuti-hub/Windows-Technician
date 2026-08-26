import psutil

from diagnostics.rules import get_memory_status


def get_memory_info():
    memory = psutil.virtual_memory()

    memory_info = {
        "total_gb": memory.total / (1024 ** 3),
        "available_gb": memory.available / (1024 ** 3),
        "used_gb": memory.used / (1024 ** 3),
        "usage_percent": memory.percent
    }

    return memory_info


def analyze_memory(memory_info):

    usage = memory_info["usage_percent"]

    status = get_memory_status(usage)

    if status == "NORMAL":

        severity = "INFO"
        finding = (
            "Memory utilization is within a normal "
            "operating range."
        )
        recommendation = (
            "No immediate memory action is required."
        )

    elif status == "ATTENTION":

        severity = "INFO"
        finding = (
            "Memory utilization is moderately elevated."
        )
        recommendation = (
            "Monitor memory usage and identify applications "
            "causing sustained memory consumption."
        )

    elif status == "WARNING":

        severity = "WARNING"
        finding = (
            "Memory usage is high and may affect "
            "system responsiveness."
        )
        recommendation = (
            "Investigate applications consuming excessive "
            "memory and close unnecessary applications."
        )

    elif status == "HIGH MEMORY PRESSURE":

        severity = "WARNING"
        finding = (
            "System memory pressure is very high."
        )
        recommendation = (
            "Close unnecessary applications and investigate "
            "the largest memory-consuming processes."
        )

    else:

        severity = "CRITICAL"
        finding = (
            "System memory pressure is critically high."
        )
        recommendation = (
            "Immediately reduce memory usage by closing "
            "unnecessary applications and investigate the "
            "cause of sustained memory pressure."
        )

    return {
        "status": status,
        "severity": severity,
        "finding": finding,
        "recommendation": recommendation
    }

def get_top_memory_processes(limit=5):
    processes = []

    for process in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            memory_usage = process.info["memory_info"].rss

            processes.append({
                "pid": process.info["pid"],
                "name": process.info["name"],
                "memory_mb": memory_usage / (1024 ** 2)
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(
        key=lambda process: process["memory_mb"],
        reverse=True
    )

    return processes[:limit]

def get_memory_by_application():
    applications = {}

    for process in psutil.process_iter(["name", "memory_info"]):
        try:
            name = process.info["name"]

            if not name:
                continue

            memory_bytes = process.info["memory_info"].rss
            memory_mb = memory_bytes / (1024 ** 2)

            if name not in applications:
                applications[name] = {
                    "process_count": 0,
                    "memory_mb": 0
                }

            applications[name]["process_count"] += 1
            applications[name]["memory_mb"] += memory_mb

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    results = []

    for name, data in applications.items():
        results.append({
            "name": name,
            "process_count": data["process_count"],
            "memory_mb": data["memory_mb"]
        })

    results.sort(
        key=lambda application: application["memory_mb"],
        reverse=True
    )

    return results[:5]

def analyze_memory_contributors(memory_by_application):

    if not memory_by_application:
        return {
            "process": None,
            "memory_mb": 0,
            "finding": "No memory contributor data is available."
        }

    top_application = memory_by_application[0]

    return {
        "process": top_application["name"],
        "memory_mb": top_application["memory_mb"],
        "finding": (
            f"{top_application['name']} is the largest grouped "
            f"memory consumer at "
            f"{top_application['memory_mb']:.2f} MB."
        )
    }

def generate_memory_diagnostics(memory_info, memory_by_application):

    memory_diagnosis = analyze_memory(memory_info)
    contributor = analyze_memory_contributors(memory_by_application)

    findings = []

    findings.append({
        "severity": memory_diagnosis["severity"],
        "category": "MEMORY",
        "message": (
            f"System memory usage is "
            f"{memory_info['usage_percent']:.1f}%. "
            f"{memory_diagnosis['finding']}"
        )
    })

    if contributor["process"] is not None:

        if memory_diagnosis["status"] == "CRITICAL":
            contributor_severity = "CRITICAL"

        elif memory_diagnosis["status"] in [
            "HIGH MEMORY PRESSURE",
            "WARNING"
        ]:
            contributor_severity = "WARNING"

        else:
            contributor_severity = "INFO"

        findings.append({
            "severity": contributor_severity,
            "category": "MEMORY CONTRIBUTOR",
            "message": contributor["finding"]
        })

    return {
        "status": memory_diagnosis["status"],
        "findings": findings,
        "recommendation": memory_diagnosis["recommendation"]
    }

if __name__ == "__main__":

    memory_info = get_memory_info()

    memory_by_application = get_memory_by_application()

    result = generate_memory_diagnostics(
        memory_info,
        memory_by_application
    )

    print("==========================================")
    print("MEMORY HEALTH TEST")
    print("==========================================")

    print(f"Memory Usage : {memory_info['usage_percent']:.1f}%")
    print(f"Status : {result['status']}")

    print()
    print("Memory Diagnostic Findings")
    print("------------------------------------------")

    for finding in result["findings"]:
        print(
            f"[{finding['severity']}] "
            f"{finding['category']} : "
            f"{finding['message']}"
        )

    print()
    print("Memory Recommendation")
    print("------------------------------------------")

    print(result["recommendation"])
    
