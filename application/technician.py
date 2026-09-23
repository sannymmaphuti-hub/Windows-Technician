# ==========================================
# Windows Technician v0.6
# APPLICATION SERVICE
# ==========================================

from copy import deepcopy

from engine.diagnostic_orchestrator import DiagnosticOrchestrator
from engine.case_decision import CaseDecision
from engine.report import generate_case_report
from engine.remediation_action_planner import RemediationActionPlanner
from engine.remediation_coordinator import RemediationCoordinator
from engine.remediation_operation_binder import (
    RemediationOperationBinder,
)
from engine.remediation_operation_registry import (
    RemediationOperationRegistry,
)
from engine.remediation_operation_selector import (
    RemediationOperationSelector,
)
from engine.remediation_operation_catalog import (
    RemediationOperationCatalog,
)
from engine.network_diagnostic_pipeline import (
    NetworkDiagnosticPipeline,
)
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCaseSynthesizer,
)
from engine.network_diagnostic_case_adapter import (
    NetworkDiagnosticCaseAdapter,
)
from engine.case_explanation import (
    CaseExplanation,
)

class Technician:

    def __init__(self):
        self.remediation_action_planner = (
            RemediationActionPlanner()
        )

        self.remediation_coordinator = (
            RemediationCoordinator()
        )

        self.diagnostic_orchestrator = (
            DiagnosticOrchestrator()
        )

        self.network_diagnostic_pipeline = (
            NetworkDiagnosticPipeline()
        )

        self.network_case_synthesizer = (
            NetworkDiagnosticCaseSynthesizer(
                self.network_diagnostic_pipeline
            )
        )

        self.network_case_adapter = (
            NetworkDiagnosticCaseAdapter()
        )

        self.network_case_explanation = (
        CaseExplanation()
        )

        self.remediation_operation_registry = (
            RemediationOperationRegistry()
        )

        self.remediation_operation_catalog = (
            RemediationOperationCatalog()
        )

        for operation_id, operation in (
            self.remediation_operation_catalog
            .get_operations()
            .items()
        ):
            self.remediation_operation_registry.register(
                operation_id,
                operation,
            )

        self.remediation_operation_binder = (
            RemediationOperationBinder(
                registry=self.remediation_operation_registry,
            )
        )

        self.remediation_operation_selector = (
            RemediationOperationSelector()
        )

        # Compatibility with existing application tests
        self.diagnostic_engine = (
            self.diagnostic_orchestrator.pipeline
        )

        self.last_result = None

    def diagnose(self):

        result = self.diagnostic_orchestrator.run()

        case = self.diagnostic_orchestrator.get_case()

        remediation_actions = (
            self.remediation_action_planner
            .create_actions_from_case(case)
        )

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

        self.last_result[
            "remediation_actions"
        ] = remediation_actions

        network_evidence = (
            result.get(
                "evidence",
                {}
            ).get(
                "NETWORK",
                {}
            )
        )

        if isinstance(network_evidence, dict):
            network_case = (
                self.network_case_synthesizer
                .synthesize(
                    network_evidence
                )
            )

            network_result = (
                self.network_case_adapter
                .to_application_result(
                    network_case
                )
            )

            network_explanation = (
                self.network_case_explanation
                .explain(
                    network_case,
                    "USER",
                )
            )

            self.last_result.update(
                network_result
            )

            self.last_result[
                "network_case_explanation"
            ] = network_explanation
        return self.last_result

    def get_network_case_explanation(
        self,
        audience,
    ):
        if self.last_result is None:
            self.diagnose()

        network_evidence = (
            self.last_result
            .get("evidence", {})
            .get("NETWORK", {})
        )

        if not isinstance(
            network_evidence,
            dict,
        ):
            return None

        network_case = (
            self.network_case_synthesizer
            .synthesize(
                network_evidence
            )
        )

        return (
            self.network_case_explanation
            .explain(
                network_case,
                audience,
            )
        )
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

        case.remediation_audit = (
            self.get_remediation_audit()
        )

        return generate_case_report(case)

    def select_remediation_operation(self, action):
        return self.remediation_operation_selector.select(action)

    def bind_remediation_operation(self, action):
        operation_id = self.select_remediation_operation(action)

        if operation_id is None:
            return None

        self.remediation_operation_binder.bind(
            action,
            operation_id,
        )

        return action

    def remediate(self, action, expected=None, observed=None):
        return self.remediation_coordinator.execute(
            action,
            expected=expected,
            observed=observed,
        )

    def authorize_remediation(self, action):
        action.authorize()

    def get_remediation_audit(self):
        return self.remediation_coordinator.audit.get_records()

