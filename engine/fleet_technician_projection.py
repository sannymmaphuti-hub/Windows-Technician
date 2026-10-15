from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.fleet_case_aggregation import FleetCaseAggregation
from engine.fleet_health_aggregation import FleetHealthAggregation
from engine.fleet_signal_correlation import FleetSignalCorrelation
from engine.fleet_finding_intelligence import FleetFindingIntelligence
from engine.fleet_root_cause_intelligence import FleetRootCauseIntelligence
from engine.fleet_recommendation_intelligence import FleetRecommendationIntelligence
from engine.fleet_prioritization import FleetPrioritization
from engine.fleet_anomaly_intelligence import FleetAnomalyIntelligence


class FleetTechnicianProjection:
    """
    Canonical V1.0 technician-facing fleet intelligence projection.

    This class composes existing fleet intelligence services into a
    deterministic, read-only technician-facing surface.

    It does not diagnose, infer new findings or root causes, create
    recommendations, authorize remediation, execute remediation,
    verify remediation, or mutate canonical fleet/case state.
    """

    def __init__(self, fleet, cases=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "fleet must be a Fleet."
            )

        if cases is None:
            cases = []

        if not isinstance(cases, (list, tuple)):
            raise ValueError(
                "cases must be a list or tuple."
            )

        for case in cases:
            if not isinstance(case, DiagnosticCase):
                raise ValueError(
                    "cases must contain DiagnosticCase objects."
                )

        self.fleet = fleet
        self.cases = list(cases)

        self.case_aggregation = FleetCaseAggregation(
            fleet,
            self.cases,
        )
        self.health = FleetHealthAggregation(
            fleet,
        )
        self.signals = FleetSignalCorrelation(
            fleet,
            self.cases,
        )
        self.findings = FleetFindingIntelligence(
            fleet,
            self.cases,
        )
        self.root_causes = FleetRootCauseIntelligence(
            fleet,
            self.cases,
        )
        self.recommendations = FleetRecommendationIntelligence()
        self.prioritization = FleetPrioritization(
            fleet,
            self.cases,
        )
        self.anomalies = FleetAnomalyIntelligence(
            fleet,
            self.cases,
        )

    def _fleet_projection(self):
        return {
            "fleet_id": self.fleet.fleet_id,
            "name": self.fleet.name,
        }

    def _recommendation_projection(self):
        return self.recommendations.projection(
            self.fleet,
            self.cases,
        )

    def overview(self):
        return {
            "health": deepcopy(
                self.health.projection()
            ),
            "cases": deepcopy(
                self.case_aggregation.projection()
            ),
        }

    def attention(self):
        prioritization = self.prioritization.projection()
        anomalies = self.anomalies.projection()

        return {
            "summary": deepcopy(
                prioritization["summary"]
            ),
            "affected_machine_ids": deepcopy(
                prioritization["affected_machine_ids"]
            ),
            "priority_counts": deepcopy(
                prioritization["priority_counts"]
            ),
            "ranked_recommendations": deepcopy(
                prioritization["ranked_recommendations"]
            ),
            "top_recommendation": deepcopy(
                prioritization["top_recommendation"]
            ),
            "machine_outliers": deepcopy(
                anomalies["machine_outliers"]
            ),
            "signal_outliers": deepcopy(
                anomalies["signal_outliers"]
            ),
            "finding_outliers": deepcopy(
                anomalies["finding_outliers"]
            ),
            "recommendation_outliers": deepcopy(
                anomalies["recommendation_outliers"]
            ),
            "anomalies": deepcopy(
                anomalies
            ),
        }

    def investigation(self):
        return {
            "signals": deepcopy(
                self.signals.projection()
            ),
            "findings": deepcopy(
                self.findings.projection()
            ),
            "root_causes": deepcopy(
                self.root_causes.projection()
            ),
            "recommendations": deepcopy(
                self._recommendation_projection()
            ),
        }

    def intelligence(self):
        return {
            "health": deepcopy(
                self.health.projection()
            ),
            "cases": deepcopy(
                self.case_aggregation.projection()
            ),
            "signals": deepcopy(
                self.signals.projection()
            ),
            "findings": deepcopy(
                self.findings.projection()
            ),
            "root_causes": deepcopy(
                self.root_causes.projection()
            ),
            "recommendations": deepcopy(
                self._recommendation_projection()
            ),
            "prioritization": deepcopy(
                self.prioritization.projection()
            ),
            "anomalies": deepcopy(
                self.anomalies.projection()
            ),
        }

    def projection(self):
        return {
            "fleet": self._fleet_projection(),
            "overview": self.overview(),
            "attention": self.attention(),
            "investigation": self.investigation(),
            "intelligence": self.intelligence(),
        }
