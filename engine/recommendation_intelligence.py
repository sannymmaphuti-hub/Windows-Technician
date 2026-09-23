from engine.recommendation import Recommendation


class RecommendationIntelligence:

    _FINDING_RECOMMENDATIONS = {
        ("MEMORY", "HIGH"): {
            "recommendation_type": "memory_review",
            "category": "MEMORY",
            "priority": "HIGH",
            "description": (
                "Review memory-intensive processes and close "
                "unnecessary applications."
            ),
            "rationale": (
                "High-severity memory findings indicate that "
                "available memory may be under significant pressure."
            ),
        },
        ("CPU", "HIGH"): {
            "recommendation_type": "cpu_review",
            "category": "CPU",
            "priority": "HIGH",
            "description": (
                "Review processes consuming significant CPU "
                "resources."
            ),
            "rationale": (
                "High-severity CPU findings indicate that CPU "
                "resources may be under significant pressure."
            ),
        },
        ("STORAGE", "HIGH"): {
            "recommendation_type": "storage_review",
            "category": "STORAGE",
            "priority": "HIGH",
            "description": (
                "Review storage usage and identify unnecessary "
                "data or applications."
            ),
            "rationale": (
                "High-severity storage findings indicate that "
                "storage resources may require attention."
            ),
        },
        ("NETWORK", "HIGH"): {
            "recommendation_type": "network_review",
            "category": "NETWORK",
            "priority": "HIGH",
            "description": (
                "Review network connectivity and diagnostic "
                "information."
            ),
            "rationale": (
                "High-severity network findings indicate that "
                "network connectivity may require attention."
            ),
        },
    }

    def generate(self, findings):
        if not isinstance(findings, list):
            raise ValueError("Findings must be a list.")

        recommendations = []
        generated_types = set()

        for finding in findings:
            category, severity = self._extract_finding_attributes(
                finding
            )

            definition = self._FINDING_RECOMMENDATIONS.get(
                (category, severity)
            )

            if definition is None:
                continue

            recommendation_type = definition["recommendation_type"]

            if recommendation_type in generated_types:
                continue

            recommendations.append(
                Recommendation(
                    recommendation_type=recommendation_type,
                    category=definition["category"],
                    priority=definition["priority"],
                    description=definition["description"],
                    rationale=definition["rationale"],
                )
            )

            generated_types.add(recommendation_type)

        return recommendations

    @staticmethod
    def _extract_finding_attributes(finding):
        if isinstance(finding, dict):
            if "category" not in finding:
                raise ValueError(
                    "Each finding must provide a category."
                )

            if "severity" not in finding:
                raise ValueError(
                    "Each finding must provide a severity."
                )

            return finding["category"], finding["severity"]

        if hasattr(finding, "category") and hasattr(
            finding, "severity"
        ):
            return finding.category, finding.severity

        raise ValueError(
            "Each finding must provide a category and severity."
        )
