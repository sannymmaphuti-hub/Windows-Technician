from copy import deepcopy

from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


class SystemWideIntelligenceProjection:
    """
    Canonical V1.0 system-wide intelligence projection boundary.

    Exposes read-only projections produced by
    SystemWideIntelligenceIntegration.

    This class does not:
    - investigate
    - analyze
    - reason
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, integration):
        if not isinstance(
            integration,
            SystemWideIntelligenceIntegration,
        ):
            raise ValueError(
                "SystemWideIntelligenceProjection requires a "
                "SystemWideIntelligenceIntegration."
            )

        self.integration = integration

    def case(self):
        return deepcopy(
            self.integration.case_projection()
        )

    def investigation(self):
        return deepcopy(
            self.integration.intelligence_projection()[
                "investigation"
            ]
        )

    def relationships(self):
        return deepcopy(
            self.integration.intelligence_projection()[
                "relationships"
            ]
        )

    def root_cause_reasoning(self):
        return deepcopy(
            self.integration.intelligence_projection()[
                "root_cause_reasoning"
            ]
        )

    def recommendations(self):
        return deepcopy(
            self.integration.intelligence_projection()[
                "recommendations"
            ]
        )

    def historical(self):
        intelligence = self.integration.intelligence_projection()

        return deepcopy(
            intelligence.get("historical", {})
        )

    def intelligence(self):
        intelligence = self.integration.intelligence_projection()

        return deepcopy(intelligence)

    def projection(self):
        return {
            "case": self.case(),
            "intelligence": self.intelligence(),
        }

    def __call__(self):
        """Return the combined intelligence projection for legacy callers."""
        return self.intelligence()
