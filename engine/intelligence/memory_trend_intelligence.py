# ==========================================
# WINDOWS TECHNICIAN v0.2
# MEMORY TREND INTELLIGENCE
# ==========================================


class MemoryTrendIntelligence:

    TREND_THRESHOLD = 5.0
    SIGNIFICANT_CHANGE = 20.0

    def analyze(self, memory_history=None):

        history = memory_history or []

        # ------------------------------------------
        # No historical data
        # ------------------------------------------

        if not history:

            return {
                "trend": "UNKNOWN",
                "change_percent": 0.0,
                "is_significant_trend": False
            }

        # ------------------------------------------
        # Single sample
        # ------------------------------------------

        if len(history) == 1:

            return {
                "trend": "UNKNOWN",
                "change_percent": 0.0,
                "is_significant_trend": False
            }

        # ------------------------------------------
        # Calculate change
        # ------------------------------------------

        first_value = history[0]
        last_value = history[-1]

        change_percent = last_value - first_value

        # ------------------------------------------
        # Determine trend
        # ------------------------------------------

        if change_percent > self.TREND_THRESHOLD:

            trend = "RISING"

        elif change_percent < -self.TREND_THRESHOLD:

            trend = "FALLING"

        else:

            trend = "STABLE"

        # ------------------------------------------
        # Determine significance
        # ------------------------------------------

        is_significant_trend = (
            abs(change_percent) >=
            self.SIGNIFICANT_CHANGE
        )

        return {
            "trend": trend,
            "change_percent": change_percent,
            "is_significant_trend": is_significant_trend
        }