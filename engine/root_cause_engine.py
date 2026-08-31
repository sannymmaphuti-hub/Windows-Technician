class RootCauseEngine:
    """Analyzes correlations and identifies possible root causes."""

    def analyze(self, correlations):
        root_causes = []

        for correlation in correlations:
            correlation_type = correlation.get("type")
            strength = correlation.get("strength")

            confidence = None

            if strength in ("HIGH", "MEDIUM", "LOW"):
                confidence = strength

            # CPU + Memory
            if (
                correlation_type == "CPU_MEMORY"
                and strength in ("HIGH", "MEDIUM", "LOW")
            ):
                root_causes.append(
                    {
                        "category": "SYSTEM",
                        "severity": "WARNING",
                        "priority": 1,
                        "confidence": confidence,
                        "message": (
                            "CPU and memory resource pressure may be contributing "
                            "to system performance degradation."
                        ),
                    }
                )

            # CPU + Process
            elif (
                correlation_type == "CPU_PROCESS"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "PROCESS",
                        "severity": "WARNING",
                        "priority": 2,
                        "confidence": confidence,
                        "message": (
                            "A process may be contributing to excessive CPU usage "
                            "and system performance degradation."
                        ),
                    }
                )

            # Memory + Process
            elif (
                correlation_type == "MEMORY_PROCESS"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "PROCESS",
                        "severity": "WARNING",
                        "priority": 3,
                        "confidence": confidence,
                        "message": (
                            "A process may be contributing to excessive memory usage "
                            "and system performance degradation."
                        ),
                    }
                )

            # Memory + Storage
            elif (
                correlation_type == "MEMORY_STORAGE"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "MEMORY",
                        "severity": "WARNING",
                        "priority": 4,
                        "confidence": confidence,
                        "message": (
                            "Memory pressure may be causing increased storage activity "
                            "and system performance degradation."
                        ),
                    }
                )

            # CPU + Storage
            elif (
                correlation_type == "CPU_STORAGE"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "STORAGE",
                        "severity": "WARNING",
                        "priority": 5,
                        "confidence": confidence,
                        "message": (
                            "CPU pressure may be associated with increased storage "
                            "activity and system performance degradation."
                        ),
                    }
                )

            # CPU + Network
            elif (
                correlation_type == "CPU_NETWORK"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "NETWORK",
                        "severity": "WARNING",
                        "priority": 6,
                        "confidence": confidence,
                        "message": (
                            "CPU pressure may be associated with network activity "
                            "and system performance degradation."
                        ),
                    }
                )

            # Memory + Network
            elif (
                correlation_type == "MEMORY_NETWORK"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "NETWORK",
                        "severity": "WARNING",
                        "priority": 7,
                        "confidence": confidence,
                        "message": (
                            "Memory pressure may be associated with network activity "
                            "and system performance degradation."
                        ),
                    }
                )

            # Storage + Network
            elif (
                correlation_type == "STORAGE_NETWORK"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "STORAGE",
                        "severity": "WARNING",
                        "priority": 8,
                        "confidence": confidence,
                        "message": (
                            "Storage pressure may be associated with network activity "
                            "and system performance degradation."
                        ),
                    }
                )

            # Network + Process
            elif (
                correlation_type == "NETWORK_PROCESS"
                and strength == "HIGH"
            ):
                root_causes.append(
                    {
                        "category": "PROCESS",
                        "severity": "WARNING",
                        "priority": 9,
                        "confidence": confidence,
                        "message": (
                            "A process may be contributing to network activity "
                            "and system performance degradation."
                        ),
                    }
                )

        # Sort root causes by priority
        root_causes.sort(
            key=lambda root_cause: root_cause["priority"]
        )

        # Deduplicate root causes by priority
        unique_root_causes = {}

        for root_cause in root_causes:
            priority = root_cause["priority"]

            if priority not in unique_root_causes:
                unique_root_causes[priority] = root_cause

        root_causes = list(unique_root_causes.values())

        return root_causes
