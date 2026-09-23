import hashlib
from engine.remediation_action import RemediationAction


class RemediationActionPlanner:
    def create_action(self, recommendation):
        if not recommendation:
            return None

        description = recommendation.get("recommendation")

        if not description:
            return None

        severity = recommendation.get("severity")

        if severity not in {"WARNING", "CRITICAL"}:
            return None

        return RemediationAction(
            action_id=self._create_action_id(
                recommendation
            ),
            description=description,
            category=recommendation.get("category"),
            severity=severity,
        )

    def create_actions(self, recommendations):
        if not recommendations:
            return []

        actions = []

        for recommendation in recommendations:
            action = self.create_action(recommendation)

            if action is not None:
                actions.append(action)

        return actions

    def create_actions_from_case(self, case):
        if case is None:
            return []

        return self.create_actions(case.recommendations)

    def _create_action_id(self, recommendation):
        category = recommendation.get("category", "")
        severity = recommendation.get("severity", "")
        description = recommendation.get("recommendation", "")

        identity = (
            f"{category}|{severity}|{description}"
        )

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()[:12]

        return f"recommendation_action_{digest}"
