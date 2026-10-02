from engine.technician_case_evidence_overview import (
    TechnicianCaseEvidenceOverview,
)
from engine.technician_case_overview import (
    TechnicianCaseOverview,
)
from engine.technician_correlation_detail import (
    TechnicianCorrelationDetail,
)
from engine.technician_evidence_findings_summary import (
    TechnicianEvidenceFindingsSummary,
)
from engine.technician_finding_detail import (
    TechnicianFindingDetail,
)
from engine.technician_recommendation_detail import (
    TechnicianRecommendationDetail,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_root_cause_detail import (
    TechnicianRootCauseDetail,
)
from engine.technician_workflow import TechnicianWorkflow


class TechnicianEvidenceView:

    def __init__(self, workflow, cycle_history):
        if not isinstance(
            workflow,
            TechnicianWorkflow,
        ):
            raise ValueError(
                "TechnicianEvidenceView requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            cycle_history,
            TechnicianRecoveryCycleHistory,
        ):
            raise ValueError(
                "TechnicianEvidenceView requires a "
                "TechnicianRecoveryCycleHistory."
            )

        if cycle_history.workflow is not workflow:
            raise ValueError(
                "Recovery cycle history belongs to a "
                "different workflow."
            )

        self._workflow = workflow
        self._cycle_history = cycle_history

    @property
    def workflow(self):
        return self._workflow

    @property
    def cycle_history(self):
        return self._cycle_history

    @property
    def case_id(self):
        return self._workflow.case.case_id

    @property
    def case_overview(self):
        return TechnicianCaseOverview(
            self._workflow,
            self._cycle_history,
        )

    @property
    def evidence_overview(self):
        return TechnicianCaseEvidenceOverview(
            self._workflow,
            self._cycle_history,
        )

    @property
    def findings_summary(self):
        return TechnicianEvidenceFindingsSummary(
            self._workflow,
            self._cycle_history,
        )

    @property
    def finding_details(self):
        return [
            TechnicianFindingDetail(
                self._workflow,
                self._cycle_history,
                finding,
            )
            for finding in self._workflow.case.findings
        ]

    @property
    def correlation_details(self):
        return [
            TechnicianCorrelationDetail(
                self._workflow,
                self._cycle_history,
                correlation,
            )
            for correlation in self._workflow.case.correlations
        ]

    @property
    def root_cause_details(self):
        return [
            TechnicianRootCauseDetail(
                self._workflow,
                self._cycle_history,
                root_cause,
            )
            for root_cause in self._workflow.case.root_causes
        ]

    @property
    def recommendation_details(self):
        return [
            TechnicianRecommendationDetail(
                self._workflow,
                self._cycle_history,
                recommendation,
            )
            for recommendation in self._workflow.case.recommendations
        ]
    