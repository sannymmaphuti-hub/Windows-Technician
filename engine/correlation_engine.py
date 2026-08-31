# ==========================================
# WINDOWS TECHNICIAN v0.3
# CORRELATION ENGINE
# ==========================================


class CorrelationEngine:

    def analyze(self, evidence):

        if not evidence:
            return []

        correlations = []

        cpu = evidence.get("CPU", {})
        memory = evidence.get("Memory", {})

        cpu_usage = cpu.get("usage_percent", 0)
        memory_usage = memory.get("usage_percent", 0)

        # ==========================================
        # CPU + MEMORY
        # ==========================================

        if cpu_usage >= 85 and memory_usage >= 85:

            if cpu_usage >= 95 and memory_usage >= 95:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "CPU_MEMORY",
                "strength": strength,
                "message": "CPU and memory pressure are correlated."
            })

        # ==========================================
        # CPU + PROCESS
        # ==========================================

        processes = evidence.get("Processes", {})

        top_process = processes.get("top_process")

        top_process_cpu = processes.get(
            "top_process_cpu_percent",
            0
        )

        if (
            cpu_usage >= 85
            and top_process
            and top_process_cpu >= 70
        ):

            if cpu_usage >= 95 and top_process_cpu >= 90:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "CPU_PROCESS",
                "strength": strength,
                "message": (
                    f"High CPU usage may be driven by "
                    f"{top_process}."
                )
            })

        # ==========================================
        # MEMORY + PROCESS
        # ==========================================

        top_process_memory = processes.get(
            "top_process_memory_percent",
            0
        )

        if (
            memory_usage >= 85
            and top_process
            and top_process_memory >= 70
        ):

            correlations.append({
                "type": "MEMORY_PROCESS",
                "strength": "HIGH",
                "message": (
                    f"High memory usage may be driven by "
                    f"{top_process}."
                )
            })

        # ==========================================
        # MEMORY + STORAGE
        # ==========================================

        storage = evidence.get("Storage", {})

        storage_usage = storage.get(
            "usage_percent",
            0
        )

        if (
            memory_usage >= 85
            and storage_usage >= 90
        ):

            if memory_usage >= 95 and storage_usage >= 95:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "MEMORY_STORAGE",
                "strength": strength,
                "message": (
                    "High memory usage and storage pressure "
                    "may be contributing to system slowdown."
                )
            })

        # ==========================================
        # CPU + STORAGE
        # ==========================================

        if (
            cpu_usage >= 85
            and storage_usage >= 90
        ):

            if cpu_usage >= 95 and storage_usage >= 95:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "CPU_STORAGE",
                "strength": strength,
                "message": (
                    "High CPU usage and storage pressure "
                    "may be contributing to system slowdown."
                )
            })

        # ==========================================
        # CPU + NETWORK
        # ==========================================

        network = evidence.get("Network", {})

        network_activity = network.get(
            "activity_percent",
            0
        )

        if (
            cpu_usage >= 85
            and network_activity >= 80
        ):

            if cpu_usage >= 95 and network_activity >= 90:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "CPU_NETWORK",
                "strength": strength,
                "message": (
                    "High CPU usage and network activity "
                    "may be contributing to system load."
                )
            })

        # ==========================================
        # MEMORY + NETWORK
        # ==========================================

        if (
            memory_usage >= 85
            and network_activity >= 80
        ):

            if memory_usage >= 95 and network_activity >= 90:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "MEMORY_NETWORK",
                "strength": strength,
                "message": (
                    "High memory usage and network activity "
                    "may be contributing to system load."
                )
            })

        # ==========================================
        # STORAGE + NETWORK
        # ==========================================

        if (
            storage_usage >= 90
            and network_activity >= 80
        ):

            if storage_usage >= 95 and network_activity >= 90:
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "STORAGE_NETWORK",
                "strength": strength,
                "message": (
                    "High storage usage and network activity "
                    "may be contributing to system slowdown."
                )
            })

        # NETWORK + PROCESS
        network = evidence.get("Network", {})
        processes = evidence.get("Processes", {})

        network_activity = network.get(
            "activity_percent",
            0
        )

        top_process = processes.get("top_process")

        top_process_network = processes.get(
            "top_process_network_percent",
            0
        )

        if (
            network_activity >= 80
            and top_process
            and top_process_network >= 70
        ):

            if (
                network_activity >= 95
                and top_process_network >= 90
            ):
                strength = "CRITICAL"
            else:
                strength = "HIGH"

            correlations.append({
                "type": "NETWORK_PROCESS",
                "strength": strength,
                "message": (
                    f"High network activity may be driven by "
                    f"{top_process}."
                )
            })

        return correlations
