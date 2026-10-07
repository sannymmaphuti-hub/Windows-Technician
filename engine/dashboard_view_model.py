from copy import deepcopy


class DashboardViewModel:
    """
    Read-only presentation model for the Windows Technician
    dashboard.

    The dashboard presents intelligence results but does not
    perform diagnosis, reasoning, recommendation generation,
    authorization, remediation, or execution.
    """

    def __init__(
        self,
        application_state,
        intelligence=None,
    ):
        if application_state is None:
            raise ValueError(
                "application_state is required."
            )

        self.application_state = application_state
        self.intelligence = (
            deepcopy(intelligence)
            if isinstance(intelligence, dict)
            else {}
        )

    def update_intelligence(self, intelligence):
        if intelligence is None:
            self.intelligence = {}
            return

        if not isinstance(intelligence, dict):
            raise ValueError(
                "intelligence must be a dictionary."
            )

        self.intelligence = deepcopy(
            intelligence
        )

    def health(self):
        health = self.intelligence.get(
            "health"
        )

        if not isinstance(health, dict):
            return {}

        return deepcopy(health)

    def findings(self):
        findings = self.intelligence.get(
            "system_findings"
        )

        if not isinstance(findings, list):
            return []

        return deepcopy(findings)

    def relationships(self):
        relationships = self.intelligence.get(
            "relationships"
        )

        if not isinstance(
            relationships,
            list,
        ):
            return []

        return deepcopy(relationships)

    def root_causes(self):
        root_causes = self.intelligence.get(
            "root_causes"
        )

        if not isinstance(
            root_causes,
            list,
        ):
            return []

        return deepcopy(root_causes)

    def recommendations(self):
        recommendations = self.intelligence.get(
            "recommendations"
        )

        if not isinstance(
            recommendations,
            list,
        ):
            return []

        return deepcopy(recommendations)

    def summary(self):
        health = self.health()

        return {
            "status": health.get(
                "status",
                "UNKNOWN",
            ),
            "health_score": health.get(
                "score"
            ),
            "finding_count": len(
                self.findings()
            ),
            "relationship_count": len(
                self.relationships()
            ),
            "root_cause_count": len(
                self.root_causes()
            ),
            "recommendation_count": len(
                self.recommendations()
            ),
            "machine_id": (
                self.application_state.active_machine_id
            ),
            "case_id": (
                self.application_state.active_case_id
            ),
        }

    def to_dict(self):
        return {
            "summary": self.summary(),
            "health": self.health(),
            "findings": self.findings(),
            "relationships": self.relationships(),
            "root_causes": self.root_causes(),
            "recommendations": self.recommendations(),
        }
