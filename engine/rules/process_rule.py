# ==========================================
# Windows Technician v0.3
# PROCESS DIAGNOSTIC RULE
# ==========================================

class ProcessRule:

    category = "PROCESS"

    CPU_THRESHOLD = 80
    MEMORY_THRESHOLD_MB = 1000

    def evaluate(self, evidence):

        processes = evidence.get(
            "processes",
            []
        )

        findings = []

        for process in processes:

            name = process.get(
                "name",
                "Unknown"
            )

            pid = process.get(
                "pid",
                0
            )

            cpu_percent = process.get(
                "cpu_percent",
                0
            )

            memory_mb = process.get(
                "memory_mb",
                0
            )

            # ------------------------------------------
            # CPU
            # ------------------------------------------

            if cpu_percent >= self.CPU_THRESHOLD:

                findings.append({

                    "severity": "WARNING",

                    "category": "PROCESS CPU",

                    "pid": pid,

                    "name": name,

                    "message": (
                        f"{name} is using "
                        f"{cpu_percent:.1f}% CPU."
                    )
                })

            # ------------------------------------------
            # MEMORY
            # ------------------------------------------

            if memory_mb >= self.MEMORY_THRESHOLD_MB:

                findings.append({

                    "severity": "WARNING",

                    "category": "PROCESS MEMORY",

                    "pid": pid,

                    "name": name,

                    "message": (
                        f"{name} is using "
                        f"{memory_mb:.2f} MB of memory."
                    )
                })

        return findings
