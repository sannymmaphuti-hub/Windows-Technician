import psutil
import time


# ==========================================================
# WINDOWS TECHNICIAN v0.2
# PROCESS DIAGNOSTIC ENGINE
# ==========================================================


def get_process_snapshot():

    processes = []

    # ------------------------------------------------------
    # Initialize CPU counters
    # ------------------------------------------------------

    for process in psutil.process_iter():

        try:
            process.cpu_percent(None)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    # ------------------------------------------------------
    # Allow CPU counters to measure activity
    # ------------------------------------------------------

    time.sleep(1)

    # ------------------------------------------------------
    # Collect process information
    # ------------------------------------------------------

    for process in psutil.process_iter(
    [
        "pid",
        "name",
        "memory_info",
        "status"
    ]
    ):

        try:

        # System Idle Process represents unused CPU capacity.
        # It must never be treated as CPU-consuming activity.
            if process.info["name"] == "System Idle Process":
                continue

            cpu_percent = process.cpu_percent(None)

            memory_info = process.info["memory_info"]

            memory_mb = memory_info.rss / (1024 ** 2)

            processes.append({
                "pid": process.info["pid"],
                "name": process.info["name"],
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "status": process.info["status"]
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return processes


# ==========================================================
# PROCESS PERSISTENCE ANALYSIS
# ==========================================================

def get_process_cpu_history(
    sample_count=5,
    interval=1
):

    history = {}

    for sample_number in range(sample_count):

        snapshot = get_process_snapshot()

        for process in snapshot:

            pid = process["pid"]

            if pid not in history:

                history[pid] = {
                    "pid": pid,
                    "name": process["name"],
                    "samples": []
                }

            history[pid]["samples"].append(
                process["cpu_percent"]
            )

        if sample_number < sample_count - 1:

            time.sleep(interval)

    return list(history.values())

def analyze_process_persistence(
    process_history,
    cpu_threshold=80,
    minimum_samples=3
):

    findings = []

    for process in process_history:

        samples = process["samples"]

        if len(samples) < minimum_samples:
            continue

        behavior = classify_cpu_behavior(
            samples,
            cpu_threshold
        )

        if behavior["classification"] != "PERSISTENT HIGH CPU":
            continue

        high_cpu_samples = [
            value
            for value in samples
            if value >= cpu_threshold
        ]

        average_cpu = (
            sum(samples)
            / len(samples)
        )

        persistence_ratio = (
            len(high_cpu_samples)
            / len(samples)
        ) * 100

        findings.append({
            "severity": "WARNING",
            "category": "PROCESS PERSISTENCE",
            "pid": process["pid"],
            "name": process["name"],
            "classification": behavior["classification"],
            "average_cpu_percent": average_cpu,
            "persistence_ratio": persistence_ratio,
            "high_cpu_samples": len(high_cpu_samples),
            "total_samples": len(samples),
            "message": (
                f"{process['name']} maintained high CPU usage "
                f"across {len(high_cpu_samples)} of "
                f"{len(samples)} samples."
            )
        })

    return findings

# ==========================================================
# CPU BEHAVIOR CLASSIFICATION
# ==========================================================

def classify_cpu_behavior(
    samples,
    cpu_threshold=80
):

    if not samples:

        return {
            "classification": "NO DATA",
            "message": "No CPU history is available."
        }

    high_cpu_samples = [
        value
        for value in samples
        if value >= cpu_threshold
    ]

    total_samples = len(samples)

    high_cpu_count = len(high_cpu_samples)

    persistence_ratio = (
        high_cpu_count / total_samples
    ) * 100

    # ------------------------------------------------------
    # Persistent high CPU
    # ------------------------------------------------------

    if persistence_ratio >= 60:

        return {
            "classification": "PERSISTENT HIGH CPU",
            "message": (
                "The process maintained high CPU usage "
                "across most samples."
            )
        }

    # ------------------------------------------------------
    # CPU spike
    # ------------------------------------------------------

    if high_cpu_count > 0:

        return {
            "classification": "CPU SPIKE",
            "message": (
                "The process experienced temporary "
                "high CPU activity."
            )
        }

    # ------------------------------------------------------
    # Normal CPU behavior
    # ------------------------------------------------------

    return {
        "classification": "NORMAL",
        "message": (
            "The process CPU activity remained "
            "within the normal range."
        )
    }

# ==========================================================
# STANDARD PROCESS ANALYSIS
# ==========================================================

def analyze_processes(processes):

    findings = []

    for process in processes:

        # --------------------------------------------------
        # Ignore Windows System Idle Process
        # --------------------------------------------------

        if process["name"] == "System Idle Process":
            continue

        # --------------------------------------------------
        # CPU
        # --------------------------------------------------

        if process["cpu_percent"] >= 80:

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS CPU",
                "pid": process["pid"],
                "name": process["name"],
                "message": (
                    f"{process['name']} is using "
                    f"{process['cpu_percent']:.1f}% CPU."
                )
            })

        # --------------------------------------------------
        # MEMORY
        # --------------------------------------------------

        if process["memory_mb"] >= 1000:

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS MEMORY",
                "pid": process["pid"],
                "name": process["name"],
                "message": (
                    f"{process['name']} is using "
                    f"{process['memory_mb']:.2f} MB of memory."
                )
            })

    return findings


# ==========================================================
# TOP PROCESSES
# ==========================================================

def get_top_processes_by_memory(
    processes,
    limit=5
):

    return sorted(
        processes,
        key=lambda process: process["memory_mb"],
        reverse=True
    )[:limit]


def get_top_processes_by_cpu(
    processes,
    limit=5
):

    valid_processes = [
        process
        for process in processes
        if process["name"] != "System Idle Process"
    ]

    return sorted(
        valid_processes,
        key=lambda process: process["cpu_percent"],
        reverse=True
    )[:limit]

# ==========================================================
# CPU BEHAVIOR REPORTING
# ==========================================================

def analyze_cpu_behavior_history(
    process_history,
    cpu_threshold=80
):

    findings = []

    for process in process_history:

        samples = process["samples"]

        behavior = classify_cpu_behavior(
            samples,
            cpu_threshold
        )

        classification = behavior["classification"]

        # --------------------------------------------------
        # Ignore normal processes
        # --------------------------------------------------

        if classification == "NORMAL":
            continue

        # --------------------------------------------------
        # CPU SPIKE
        # --------------------------------------------------

        if classification == "CPU SPIKE":

            findings.append({
                "severity": "INFO",
                "category": "PROCESS CPU BEHAVIOR",
                "pid": process["pid"],
                "name": process["name"],
                "classification": classification,
                "message": (
                    f"{process['name']} experienced "
                    f"temporary high CPU activity."
                )
            })

        # --------------------------------------------------
        # PERSISTENT HIGH CPU
        # --------------------------------------------------

        elif classification == "PERSISTENT HIGH CPU":

            findings.append({
                "severity": "WARNING",
                "category": "PROCESS CPU BEHAVIOR",
                "pid": process["pid"],
                "name": process["name"],
                "classification": classification,
                "message": (
                    f"{process['name']} maintained "
                    f"high CPU activity across most samples."
                )
            })

    return findings


# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    print("==========================================")
    print("PROCESS PERSISTENCE TEST")
    print("==========================================")

    print()
    print("Collecting process CPU history...")
    print("Please wait...")

    history = get_process_cpu_history(
        sample_count=5,
        interval=1
    )

    findings = analyze_process_persistence(
        history
    )

    print()
    print("Persistent CPU Findings")
    print("------------------------------------------")

    if not findings:

        print(
            "No persistent high CPU activity detected."
        )

    else:

        for finding in findings:

            print(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

            print(
                f"    Average CPU : "
                f"{finding['average_cpu_percent']:.1f}%"
            )

            print(
                f"    Persistence Ratio : "
                f"{finding['persistence_ratio']:.1f}%"
            )

            print(
                f"    High CPU Samples : "
                f"{finding['high_cpu_samples']}/"
                f"{finding['total_samples']}"
            )


        print()
    print("==========================================")
    print("CPU BEHAVIOR REPORTING TEST")
    print("==========================================")

    behavior_test_history = [
        {
            "pid": 2001,
            "name": "NormalProcess.exe",
            "samples": [5, 10, 8, 12, 7]
        },
        {
            "pid": 2002,
            "name": "SpikeProcess.exe",
            "samples": [5, 92, 8, 7, 6]
        },
        {
            "pid": 2003,
            "name": "PersistentProcess.exe",
            "samples": [85, 88, 91, 86, 90]
        }
    ]

    behavior_findings = analyze_cpu_behavior_history(
        behavior_test_history
    )

    print()
    print("CPU Behavior Findings")
    print("------------------------------------------")

    if not behavior_findings:

        print("No abnormal CPU behavior detected.")

    else:

        for finding in behavior_findings:

            print(
                f"[{finding['severity']}] "
                f"{finding['category']} : "
                f"{finding['message']}"
            )

            print(
                f"    Classification : "
                f"{finding['classification']}"
            )
