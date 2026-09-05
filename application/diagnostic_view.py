# ==========================================
# WINDOWS TECHNICIAN v0.4
# DIAGNOSTIC VIEW
# ==========================================

from copy import deepcopy


class DiagnosticView:

    def __init__(self, result):
        self.result = deepcopy(result)

        self.evidence = deepcopy(
        self.result.get("evidence", {})
        )

        diagnosis = self.result.get("diagnosis", {})
        diagnostic_case = self.result.get("diagnostic_case", {})

        self.status = diagnosis.get("status")
        self.total_findings = diagnosis.get("total_findings", 0)
        self.findings = deepcopy(
            diagnosis.get("findings", [])
        )
        self.correlations = deepcopy(
            diagnosis.get("correlations", [])
        )
        self.root_causes = deepcopy(
            diagnosis.get("root_causes", [])
        )
        self.recommendations = deepcopy(
            diagnosis.get("recommendations", [])
        )

        self.root_cause_candidates = deepcopy(
            diagnostic_case.get("root_cause_candidates", [])
        )
        self.primary_root_cause = deepcopy(
            diagnostic_case.get("primary_root_cause")
        )

        self.case_decision = deepcopy(
            self.result.get("case_decision", {})
        )

        self.process_intelligence = deepcopy(
            diagnostic_case.get("process_intelligence")
        )
        self.memory_intelligence = deepcopy(
            diagnostic_case.get("memory_intelligence")
        )
        self.memory_history = deepcopy(
            diagnostic_case.get("memory_history", [])
        )
        self.memory_trend_intelligence = deepcopy(
            diagnostic_case.get("memory_trend_intelligence")
        )
        self.memory_temporal_intelligence = deepcopy(
            diagnostic_case.get("memory_temporal_intelligence")
        )
        self.memory_diagnostic_intelligence = deepcopy(
            diagnostic_case.get("memory_diagnostic_intelligence")
        )