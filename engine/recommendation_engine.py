from engine.recommendation_rule import RecommendationRule
from engine.finding import Finding
from engine.legacy_finding_adapter import LegacyFindingAdapter


class RecommendationEngine:

    LEGACY_RECOMMENDATIONS = {

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

    def __init__(self, adapter=None):
        self._rules = []
        self._legacy_finding_adapter = (
            adapter if adapter is not None
            else LegacyFindingAdapter()
        )

    def register_rule(self, rule):
        if not isinstance(rule, RecommendationRule):
            raise ValueError("rule must be a RecommendationRule.")

        self._rules.append(rule)

    def evaluate(self, finding):
        recommendations = []

        for rule in self._rules:
            if rule.matches(finding):
                recommendations.append(
                    rule.create_recommendation(finding)
                )

        return recommendations

    def get_recommendations(self, findings):
        recommendations = []

        for finding in findings:

            if isinstance(finding, Finding):
                recommendations.extend(
                    self.evaluate(finding)
                )
                continue

            if isinstance(finding, dict):

                if self._rules:
                    finding_object = (
                        self._convert_legacy_finding(finding)
                    )

                    if finding_object is not None:
                        recommendations.extend(
                            self.evaluate(finding_object)
                        )

                    continue

                recommendation = (
                    self._get_legacy_recommendation(
                        finding
                    )
                )

                if recommendation is not None:
                    recommendations.append(
                        recommendation
                    )

        return recommendations

    def _convert_legacy_finding(self, finding):
        return self._legacy_finding_adapter.convert(finding)

    def _get_legacy_recommendation(self, finding):

        category = finding.get("category")
        severity = finding.get("severity")

        category_recommendations = (
            self.LEGACY_RECOMMENDATIONS.get(
                category,
                {}
            )
        )

        recommendation = category_recommendations.get(
            severity
        )

        if recommendation is None:
            return None

        return {
            "category": category,
            "severity": severity,
            "recommendation": recommendation,
        }

