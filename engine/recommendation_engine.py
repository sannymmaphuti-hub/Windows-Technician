# ==========================================
# Windows Technician v0.3
# RECOMMENDATION ENGINE
# ==========================================


class RecommendationEngine:

    RECOMMENDATIONS = {

        "CPU": {
            "WARNING": (
                "Review CPU-intensive processes and "
                "close unnecessary applications."
            ),

            "CRITICAL": (
                "Identify processes with sustained high CPU "
                "utilization and investigate the highest consumer."
            )
        },

        "MEMORY": {
            "WARNING": (
                "Review memory-intensive processes and "
                "close unnecessary applications."
            ),

            "CRITICAL": (
                "Investigate excessive memory usage and "
                "identify processes consuming unusually large amounts of RAM."
            )
        },

        "STORAGE": {
            "WARNING": (
                "Free disk space by removing unnecessary files "
                "and reviewing large applications or temporary data."
            ),

            "CRITICAL": (
                "Free disk space immediately and investigate "
                "large files, applications, or temporary data."
            )
        }
    }

    def get_recommendation(self, finding):

        category = finding.get("category")
        severity = finding.get("severity")

        category_recommendations = self.RECOMMENDATIONS.get(
            category,
            {}
        )

        return category_recommendations.get(
            severity
        )

    def get_recommendations(self, findings):

        recommendations = []

        for finding in findings:

            recommendation = self.get_recommendation(
                finding
            )

            if recommendation is not None:

                recommendations.append({
                    "category": finding["category"],
                    "severity": finding["severity"],
                    "recommendation": recommendation
                })

        return recommendations
