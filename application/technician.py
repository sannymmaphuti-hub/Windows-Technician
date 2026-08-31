# ==========================================
# WINDOWS TECHNICIAN v0.3
# APPLICATION SERVICE
# ==========================================

from copy import deepcopy

from engine.diagnostic_orchestrator import DiagnosticOrchestrator
from engine.case_decision import CaseDecision
from engine.report import generate_case_report


class Technician:

    def __init__(self):

        self.diagnostic_orchestrator = (
            DiagnosticOrchestrator()
        )

        # Compatibility with existing application tests
        self.diagnostic_engine = (
            self.diagnostic_orchestrator.pipeline
        )

        self.last_result = None

    def diagnose(self):

        result = self.diagnostic_orchestrator.run()

        case = self.diagnostic_orchestrator.get_case()

        case_decision = CaseDecision(case).evaluate()

        diagnostic_case = {
            "evidence": deepcopy(
                case.evidence
            ),

            "findings": deepcopy(
                case.findings
            ),

            "correlations": deepcopy(
                case.correlations
            ),

            "root_causes": deepcopy(
                case.root_causes
            ),

            "root_cause_candidates": deepcopy(
                case.root_cause_candidates
            ),

            "primary_root_cause": deepcopy(
                case.primary_root_cause
            ),

            "recommendations": deepcopy(
                case.recommendations
            ),

            "status": deepcopy(
                case.status
            ),

            "process_intelligence": deepcopy(
                case.process_intelligence
            ),

            "memory_intelligence": deepcopy(
                case.memory_intelligence
            ),

            "memory_history": deepcopy(
                case.memory_history
            ),

            "memory_trend_intelligence": deepcopy(
                case.memory_trend_intelligence
            ),

            "memory_temporal_intelligence": deepcopy(
                case.memory_temporal_intelligence
            ),

            "memory_diagnostic_intelligence": deepcopy(
                case.memory_diagnostic_intelligence
            )
        }

        self.last_result = result

        self.last_result[
            "diagnostic_case"
        ] = diagnostic_case

        self.last_result[
            "case_decision"
        ] = deepcopy(case_decision)

        return self.last_result

    def get_status(self):

        if self.last_result is None:

            self.diagnose()

        return self.last_result[
            "diagnosis"
        ][
            "status"
        ]

    def get_primary_issue(self):

        if self.last_result is None:

            self.diagnose()

        diagnosis = self.last_result[
            "diagnosis"
        ]

        findings = diagnosis.get(
            "findings",
            []
        )

        if not findings:

            return {
                "status": "HEALTHY",
                "category": "SYSTEM",
                "issue": (
                    "No significant system issue detected."
                ),
                "severity": "INFO",
                "priority_score": 0,
                "reason": (
                    "No significant diagnostic issue "
                    "was detected."
                )
            }

        highest_priority = max(
            findings,
            key=lambda finding: (
                finding.get(
                    "priority_score",
                    0
                )
            )
        )

        return {
            "status": highest_priority.get(
                "severity",
                "INFO"
            ),

            "category": highest_priority.get(
                "category",
                "SYSTEM"
            ),

            "issue": highest_priority.get(
                "issue",
                highest_priority.get(
                    "message",
                    "Unknown issue"
                )
            ),

            "severity": highest_priority.get(
                "severity",
                "INFO"
            ),

            "priority_score": highest_priority.get(
                "priority_score",
                0
            ),

            "reason": highest_priority.get(
                "reason",
                highest_priority.get(
                    "message",
                    "No diagnostic explanation "
                    "available."
                )
            )
        }

    def get_report(self):

        if self.last_result is None:
            self.diagnose()

        case = self.diagnostic_orchestrator.get_case()

        return generate_case_report(case)
