# ==========================================
# Windows Technician v0.6
# MEMORY TEMPORAL INTELLIGENCE
# ==========================================


class MemoryTemporalIntelligence:

    MEMORY_WARNING_THRESHOLD = 80
    MEMORY_CRITICAL_THRESHOLD = 90

    PERSISTENCE_THRESHOLD = 0.60
    SPIKE_MULTIPLIER = 1.50

    def analyze(
        self,
        system_memory_percent,
        process,
        memory_history=None
    ):

        if process is None:
            return None

        process_name = process.get(
            "name",
            "Unknown"
        )

        process_memory = process.get(
            "memory_mb",
            0
        )

        pid = process.get(
            "pid",
            0
        )

        history = memory_history or []

        result = {
            "pid": pid,
            "name": process_name,
            "process_memory_mb": process_memory,
            "system_memory_percent": system_memory_percent,
        }

        # ------------------------------------------
        # No historical data
        # ------------------------------------------

        if not history:

            result["behavior"] = "UNKNOWN"
            result["persistence_ratio"] = 0.0
            result["is_sustained_consumer"] = False

            return result

        # ------------------------------------------
        # Calculate persistence
        # ------------------------------------------

        high_memory_samples = [
            value
            for value in history
            if value >= process_memory * 0.80
        ]

        persistence_ratio = (
            len(high_memory_samples) / len(history)
        )

        result["persistence_ratio"] = persistence_ratio

        # ------------------------------------------
        # Detect memory spike
        # ------------------------------------------

        historical_average = (
            sum(history[:-1]) / len(history[:-1])
            if len(history) > 1
            else history[0]
        )

        is_spike = (
            process_memory >=
            historical_average * self.SPIKE_MULTIPLIER
        )

        # ------------------------------------------
        # Determine behavior
        # ------------------------------------------

        if is_spike:

            behavior = "SPIKE"

        elif (
            persistence_ratio >= self.PERSISTENCE_THRESHOLD
            and system_memory_percent >= self.MEMORY_WARNING_THRESHOLD
        ):

            behavior = "PERSISTENT"

        else:

            behavior = "NORMAL"

        result["behavior"] = behavior

        # ------------------------------------------
        # Determine sustained consumer
        # ------------------------------------------

        result["is_sustained_consumer"] = (
            behavior == "PERSISTENT"
            and system_memory_percent >=
            self.MEMORY_WARNING_THRESHOLD
        )

        return result
