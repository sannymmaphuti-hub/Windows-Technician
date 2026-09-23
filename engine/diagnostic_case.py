# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC CASE
# ==========================================

from copy import deepcopy
from engine.recommendation_intelligence import RecommendationIntelligence


class DiagnosticCase:

    def __init__(self):

        # ==========================================
        # V0.6 CASE IDENTITY
        # ==========================================

        from uuid import uuid4

        self.case_id = str(uuid4())

        # ==========================================
        # V0.6 CASE LIFECYCLE
        # ==========================================

        self.lifecycle_state = "OPEN"

        # ==========================================
        # V0.6 DIAGNOSTIC COMPLETENESS
        # ==========================================

        self.diagnostic_completeness = "INCOMPLETE"

        # ==========================================
        # CORE DIAGNOSTIC DATA
        # ==========================================

        self.evidence = {}

        # ==========================================
        # V0.6 OBSERVATIONS
        # ==========================================

        self.observations = []

        # ==========================================
        # V0.6 SIGNALS
        # ==========================================

        self.signals = []

        self.findings = []
        self.correlations = []
        self.root_causes = []
        self.recommendations = []
        self.status = "NORMAL"

        # ==========================================
        # PROCESS INTELLIGENCE
        # ==========================================

        self.process_intelligence = None

        # ==========================================
        # MEMORY INTELLIGENCE
        # ==========================================

        self.memory_intelligence = None

        # ==========================================
        # MEMORY HISTORY
        # ==========================================

        self.memory_history = []

        # ==========================================
        # MEMORY TREND INTELLIGENCE
        # ==========================================

        self.memory_trend_intelligence = None

        # ==========================================
        # MEMORY TEMPORAL INTELLIGENCE
        # ==========================================

        self.memory_temporal_intelligence = None

        # ==========================================
        # MEMORY DIAGNOSTIC INTELLIGENCE
        # ==========================================

        self.memory_diagnostic_intelligence = None

        # ==========================================
        # ROOT CAUSE INTELLIGENCE
        # ==========================================

        self.root_cause_candidates = []
        self.primary_root_cause = None


    # ==========================================
    # CORE DATA SETTERS
    # ==========================================


    def set_evidence(self, evidence):

        self.evidence = deepcopy(evidence)


    def set_observations(self, observations):

        self.observations = deepcopy(
            observations
        )


    def set_signals(self, signals):

        self.signals = deepcopy(
            signals
        )


    def set_findings(self, findings):

        self.findings = deepcopy(findings)


    def set_correlations(self, correlations):

        self.correlations = deepcopy(correlations)


    def set_root_causes(self, root_causes):

        self.root_causes = deepcopy(root_causes)


    def set_recommendations(self, recommendations):

        self.recommendations = deepcopy(recommendations)


    # ==========================================
    # PROCESS INTELLIGENCE
    # ==========================================

    def set_process_intelligence(
        self,
        intelligence
    ):

        self.process_intelligence = deepcopy(
            intelligence
        )


    # ==========================================
    # MEMORY INTELLIGENCE
    # ==========================================

    def set_memory_intelligence(
        self,
        intelligence
    ):

        self.memory_intelligence = deepcopy(
            intelligence
        )


    # ==========================================
    # MEMORY HISTORY
    # ==========================================

    def set_memory_history(
        self,
        history
    ):

        self.memory_history = deepcopy(
            history
        )


    # ==========================================
    # MEMORY TREND INTELLIGENCE
    # ==========================================

    def set_memory_trend_intelligence(
        self,
        intelligence
    ):

        self.memory_trend_intelligence = deepcopy(
            intelligence
        )


    # ==========================================
    # MEMORY TEMPORAL INTELLIGENCE
    # ==========================================

    def set_memory_temporal_intelligence(
        self,
        intelligence
    ):

        self.memory_temporal_intelligence = deepcopy(
            intelligence
        )


    # ==========================================
    # MEMORY DIAGNOSTIC INTELLIGENCE
    # ==========================================

    def set_memory_diagnostic_intelligence(
        self,
        intelligence
    ):

        self.memory_diagnostic_intelligence = deepcopy(
            intelligence
        )


    # ==========================================
    # ROOT CAUSE CANDIDATES
    # ==========================================

    def set_root_cause_candidates(
        self,
        candidates
    ):

        self.root_cause_candidates = deepcopy(
            candidates
        )


    # ==========================================
    # PRIMARY ROOT CAUSE
    # ==========================================

    def set_primary_root_cause(
        self,
        root_cause
    ):

        self.primary_root_cause = deepcopy(
            root_cause
        )


    # ==========================================
    # DIAGNOSTIC STATUS
    # ==========================================

    def set_status(
        self,
        status
    ):

        self.status = status

    def generate_recommendations(self):
        intelligence = RecommendationIntelligence()

        recommendations = intelligence.generate(
            findings=self.findings
        )

        self.recommendations = recommendations

        return recommendations
