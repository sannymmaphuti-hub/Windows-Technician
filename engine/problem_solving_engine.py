
from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from engine.windows_diagnostic_dispatcher import (
    WindowsDiagnosticDispatcher,
)
from engine.windows_diagnostic_investigation_coordinator import (
    WindowsDiagnosticInvestigationCoordinator,
)
from engine.windows_diagnostic_result import (
    WindowsDiagnosticResult,
)
from engine.remediation_decision_boundary import RemediationDecisionBoundary
from engine.recommendation_remediation_adapter import (
    RecommendationRemediationAdapter,
)
from engine.remediation_action_planner import RemediationActionPlanner
from engine.remediation_coordinator import RemediationCoordinator
from engine.technician_verification import TechnicianVerification
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from packaging.remediation_authorization import (
    AuthorizationState,
    RemediationAuthorization,
    authorize,
    deny,
    unauthorized,
)
from engine.windows_diagnostic_result_normalizer import (
    WindowsDiagnosticResultNormalizer,
)


class ProblemSolvingState:
    PENDING = "PENDING"
    INVESTIGATING = "INVESTIGATING"
    DIAGNOSED = "DIAGNOSED"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    REMEDIATING = "REMEDIATING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"


from engine.windows_diagnostic_result_normalizer import WindowsDiagnosticResultNormalizer

class ProductionProblemSolvingEngine:
    PROJECTION_SCHEMA_VERSION = "1.0"
    """
    Canonical V1.0 production problem-solving orchestration boundary.

    This object composes existing Windows Technician capabilities.

    It does NOT create parallel implementations of:
    - diagnostic engines
    - DiagnosticCase
    - investigation
    - root-cause reasoning
    - recommendations
    - authorization
    - remediation execution
    - verification
    - recovery
    """

    def __init__(
        self,
        case,
        workflow,
        diagnostic_registry,
        dispatcher=None,
        coordinator=None,
    ):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "ProductionProblemSolvingEngine requires a DiagnosticCase."
            )

        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "ProductionProblemSolvingEngine requires a "
                "TechnicianWorkflow."
            )

        if not isinstance(
            diagnostic_registry,
            WindowsDiagnosticEngineRegistry,
        ):
            raise ValueError(
                "ProductionProblemSolvingEngine requires a "
                "WindowsDiagnosticEngineRegistry."
            )

        if workflow.case is not case:
            raise ValueError(
                "workflow must reference the supplied DiagnosticCase."
            )

        if dispatcher is None:
            dispatcher = WindowsDiagnosticDispatcher()

        if coordinator is None:
            coordinator = WindowsDiagnosticInvestigationCoordinator()

        if not hasattr(dispatcher, "dispatch"):
            raise ValueError(
                "dispatcher must provide a dispatch() method."
            )

        if not hasattr(coordinator, "attach_result"):
            raise ValueError(
                "coordinator must provide an attach_result() method."
            )

        self.case = case
        self.workflow = workflow
        self.diagnostic_registry = diagnostic_registry
        self.dispatcher = dispatcher
        self.coordinator = coordinator
        self.decision_boundary = RemediationDecisionBoundary()
        self.remediation_coordinator = RemediationCoordinator()
        self.verification = TechnicianVerification(workflow=self.workflow)
        self._verification_result = None
        self._last_remediation_result = None
        self.recovery_history = TechnicianRecoveryCycleHistory(
            workflow=self.workflow
        )
        self._state = ProblemSolvingState.PENDING
        self._result = None
        self._failure = None
        self._domain_results = {}
        self._domain_failures = {}

        self.remediation_adapter = (
            RecommendationRemediationAdapter()
        )
        self.remediation_planner = (
            RemediationActionPlanner()
        )
        self._remediation_actions = {}
        self._authorizations = {}

    @property
    def state(self):
        return self._state

    @property
    def result(self):
        return deepcopy(self._result)

    @property
    def failure(self):
        return deepcopy(self._failure)

    @property
    def domain_results(self):
        return deepcopy(self._domain_results)

    @property
    def domain_failures(self):
        return deepcopy(self._domain_failures)

    @property
    def remediation_actions(self):
        return dict(self._remediation_actions)
    @property
    def authorizations(self):
        return deepcopy(self._authorizations)

    @staticmethod
    def _collect_network_evidence():
        """Collect and adapt real network-interface evidence."""
        import psutil

        from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
        from engine.collectors.network_collector import NetworkCollector
        from engine.network_diagnostic_evidence_adapter import (
            NetworkDiagnosticEvidenceAdapter,
        )

        evidence = NetworkCollector().collect()
        interface_stats = psutil.net_if_stats()

        for adapter in evidence.get("adapters", []):
            stats = interface_stats.get(adapter.get("name"))
            adapter["is_up"] = bool(stats and stats.isup)

        adaptive_result = AdaptiveDiagnosticResult(
            evidence=evidence,
            decisions=[],
            actions=[],
            steps=0,
            stopped_reason="NO_DECISION",
        )

        return NetworkDiagnosticEvidenceAdapter().convert(adaptive_result)

    def dispatch_domain(self, domain, evidence=None):
        normalized = (
            domain.strip().upper()
            if isinstance(domain, str)
            else None
        )

        if not self.diagnostic_registry.has_engine(normalized):
            raise ValueError(
                f"Unsupported Windows diagnostic domain: {domain!r}"
            )

        if evidence is None and normalized == "NETWORK":
            evidence = self._collect_network_evidence()

        if evidence is None:
            result = self.dispatcher.dispatch(normalized)
        else:
            result = self.dispatcher.dispatch(
                normalized,
                evidence=evidence,
            )

        self._result = (
            result
            if isinstance(
                result,
                WindowsDiagnosticResult,
            )
            else deepcopy(result)
        )

        self._state = ProblemSolvingState.DIAGNOSED

        self._domain_results[normalized] = (
            result
            if isinstance(
                result,
                WindowsDiagnosticResult,
            )
            else deepcopy(result)
        )

        self._domain_failures.pop(normalized, None)

        return deepcopy(result)

    def execute_domains(self, domains, evidence=None):
        """
        Execute multiple registered Windows diagnostic domains.

        Each domain is isolated from the others. A failure in one
        domain is recorded and does not prevent subsequent domains
        from executing.

        Returns a defensive execution summary containing:
        - successful domain results
        - isolated domain failures
        """
        if not isinstance(domains, (list, tuple, set)):
            raise ValueError(
                "domains must be a list, tuple, or set."
            )

        normalized_domains = []

        for domain in domains:
            normalized = (
                domain.strip().upper()
                if isinstance(domain, str)
                else None
            )

            if not self.diagnostic_registry.has_engine(normalized):
                raise ValueError(
                    f"Unsupported Windows diagnostic domain: {domain!r}"
                )

            if normalized not in normalized_domains:
                normalized_domains.append(normalized)

        for domain in normalized_domains:
            try:
                result = self.dispatch_domain(
                    domain,
                    evidence=evidence,
                )

                if domain not in self._domain_results:
                    self._domain_results[domain] = (
                        result
                        if isinstance(
                            result,
                            WindowsDiagnosticResult,
                        )
                        else deepcopy(result)
                    )

                self._domain_failures.pop(domain, None)

            except Exception as error:
                self._domain_failures[domain] = {
                    "type": type(error).__name__,
                    "message": str(error),
                }

        if self._domain_results:
            self._state = ProblemSolvingState.DIAGNOSED
        elif normalized_domains:
            self._state = ProblemSolvingState.FAILED

        return {
            "results": self.domain_results,
            "failures": self.domain_failures,
        }

    def aggregate_domain_results(self):
        """
        Aggregate all successful domain results into one
        canonical WindowsDiagnosticResult.

        Domain failures remain isolated in domain_failures
        and are never converted into diagnostic findings.
        """
        if not self._domain_results:
            raise ValueError(
                "No successful domain results are available "
                "for aggregation."
            )

        observations = []
        signals = []
        findings = []
        correlations = []
        candidates = []
        recommendations = []
        confidences = []
        primary_cause = None

        for result in self._domain_results.values():
            canonical = (
                WindowsDiagnosticResultNormalizer.normalize(
                    result
                )
            )

            observations.extend(
                canonical.observations
            )
            signals.extend(
                canonical.signals
            )
            findings.extend(
                canonical.findings
            )
            correlations.extend(
                canonical.correlations
            )
            candidates.extend(
                canonical.candidates
            )
            recommendations.extend(
                canonical.recommendations
            )
            confidences.extend(
                canonical.confidences
            )

            if (
                primary_cause is None
                and canonical.primary_cause is not None
            ):
                primary_cause = canonical.primary_cause

        aggregated = WindowsDiagnosticResult(
            observations=observations,
            signals=signals,
            findings=findings,
            correlations=correlations,
            candidates=candidates,
            primary_cause=primary_cause,
            recommendations=recommendations,
            confidences=confidences,
        )

        self._result = aggregated
        self._state = ProblemSolvingState.DIAGNOSED

        return aggregated

    def evaluate_action_requirement(self):
        """
        Evaluate canonical recommendations through the existing
        RemediationDecisionBoundary.

        This method determines whether action is required.
        It does not authorize, execute, or verify remediation.
        """
        if self._result is None:
            raise ValueError(
                "No diagnostic result is available for "
                "action evaluation."
            )

        canonical = (
            WindowsDiagnosticResultNormalizer.normalize(
                self._result
            )
        )

        decisions = []

        for recommendation in canonical.recommendations:
            decision = self.decision_boundary.evaluate(
                recommendation
            )

            decisions.append(decision)

            if decision.eligible:
                if (
                    self.workflow.state
                    is WorkflowState.DIAGNOSED
                ):
                    self.workflow.require_action()

                self._state = (
                    ProblemSolvingState.ACTION_REQUIRED
                )

                return {
                    "action_required": True,
                    "decisions": decisions,
                }

        self._state = ProblemSolvingState.DIAGNOSED

        return {
            "action_required": False,
            "decisions": decisions,
        }
    def prepare_remediation_authorization(self):
        # Prepare canonical remediation actions and safe default
        # authorization records for eligible recommendations.
        #
        # This method does not authorize, bind, execute, or verify
        # remediation.

        if self._result is None:
            raise ValueError(
                "No diagnostic result is available for "
                "remediation authorization preparation."
            )

        canonical = (
            WindowsDiagnosticResultNormalizer.normalize(
                self._result
            )
        )

        actions = {}
        authorizations = {}

        for recommendation in canonical.recommendations:
            decision = self.decision_boundary.evaluate(
                recommendation
            )

            if not decision.eligible:
                continue

            planner_input = (
                self.remediation_adapter.to_planner_input(
                    recommendation
                )
            )

            action = self.remediation_planner.create_action(
                planner_input
            )

            if action is None:
                continue

            actions[action.action_id] = action
            authorizations[action.action_id] = (
                unauthorized(action.action_id)
            )

        self._remediation_actions = actions
        self._authorizations = authorizations

        return {
            "actions": self.remediation_actions,
            "authorizations": self.authorizations,
            "execution_available": self._execution_boundary_available(),
        }

    def authorize_remediation(
        self,
        action_id,
        *,
        technician=False,
    ):
        # Explicit authorization boundary.
        # This does not execute or bind remediation.

        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError(
                "action_id must be a non-empty string."
            )

        if action_id not in self._remediation_actions:
            raise ValueError(
                f"Unknown remediation action: {action_id!r}"
            )

        authorization = authorize(
            action_id,
            technician=technician,
        )

        self._authorizations[action_id] = authorization

        return authorization

    def deny_remediation(
        self,
        action_id,
        *,
        technician=False,
    ):
        # Explicit denial boundary.
        # This does not execute or remove the action.

        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError(
                "action_id must be a non-empty string."
            )

        if action_id not in self._remediation_actions:
            raise ValueError(
                f"Unknown remediation action: {action_id!r}"
            )

        authorization = deny(
            action_id,
            technician=technician,
        )

        self._authorizations[action_id] = authorization

        return authorization

    def authorization_for(self, action_id):
        # Return the canonical authorization for a prepared action.

        if action_id not in self._authorizations:
            raise ValueError(
                f"Unknown remediation action: {action_id!r}"
            )

        return deepcopy(
            self._authorizations[action_id]
        )

    def authorization_allows_execution(self, action_id):
        # Read-only authorization gate.
        # This method never executes remediation.

        authorization = self.authorization_for(
            action_id
        )

        return (
            authorization.state
            is AuthorizationState.AUTHORIZED
        )
    @property
    def verification_result(self):
        """Return a defensive copy of the canonical verification payload."""
        if self._verification_result is None:
            return None
        return deepcopy(self._verification_result)

    @property
    def last_remediation_result(self):
        if self._last_remediation_result is None:
            return None
        return deepcopy(self._last_remediation_result)

    @property
    def verification_complete(self):
        """Return whether the canonical verification lifecycle is complete."""
        return self.verification.is_complete

    def verify_remediation(self, result=None, expected=None, observed=None):
        """
        Verify the most recent remediation through the canonical
        TechnicianVerification boundary.

        Verification is deliberately separate from remediation execution.
        """
        if result is None:
            result = self._last_remediation_result

        if result is None:
            raise ValueError(
                "A remediation result is required for verification."
            )

        if expected is None:
            raise ValueError(
                "Expected condition is required for verification."
            )

        if observed is None:
            raise ValueError(
                "Observed condition is required for verification."
            )

        if self.workflow.state is not WorkflowState.VERIFYING:
            raise ValueError(
                "Remediation can only be verified while workflow is VERIFYING."
            )

        if not self.verification.is_active:
            self.verification.start()

        verified = self.verification.verify(
            result=result,
            expected=expected,
            observed=observed,
        )

        canonical_verification = self.verification.verification_result

        if canonical_verification is None:
            raise RuntimeError(
                "Canonical verification produced no verification result."
            )

        self._verification_result = canonical_verification.verification_result

        if verified:
            self._state = ProblemSolvingState.RESOLVED
        else:
            self._state = ProblemSolvingState.ACTION_REQUIRED

        return {
            "verified": verified,
            "verification_result": deepcopy(self._verification_result),
            "workflow_state": self.workflow.state,
            "lifecycle_history": [
                {
                    "from": previous_state.value,
                    "to": new_state.value,
                }
                for previous_state, new_state in self.workflow.history
            ],
            "state": self.state,
        }
    def execute_remediation(
        self,
        action_id,
        expected=None,
        observed=None,
    ):
        # Phase 7.9 execution boundary.
        #
        # Authorization is checked through the immutable
        # RemediationAuthorization record first.
        #
        # This method never binds an operation. The operation
        # must already have been explicitly bound through the
        # canonical RemediationOperationBinder path.

        if not isinstance(action_id, str) or not action_id.strip():
            raise ValueError(
                "action_id must be a non-empty string."
            )

        action = self._remediation_actions.get(action_id)

        if action is None:
            raise ValueError(
                f"Unknown remediation action: {action_id!r}"
            )

        authorization = self.authorization_for(action_id)

        if not self.authorization_allows_execution(action_id):
            raise PermissionError(
                f"Remediation action {action_id!r} is not authorized."
            )

        if action.operation is None:
            raise ValueError(
                f"Remediation action {action_id!r} has no "
                "bound operation."
            )

        if self.workflow.state is WorkflowState.DIAGNOSED:
            self.workflow.require_action()

        if self.workflow.state is WorkflowState.ACTION_REQUIRED:
            self.workflow.start_remediation()

        # Bridge the immutable production authorization into the
        # existing RemediationAction execution contract.
        #
        # The operation itself is never created or bound here.
        if (
            action.requires_authorization
            and action.authorization_status != "AUTHORIZED"
        ):
            action.authorize()

        result = self.remediation_coordinator.execute(
            action,
            expected=expected,
            observed=observed,
        )

        self._last_remediation_result = result

        if result.execution_status == "EXECUTED":
            if (
                expected is not None
                and observed is not None
            ):
                self.workflow.start_verification()
            else:
                self.workflow.start_verification()
        elif result.execution_status == "FAILED":
            if not self.workflow.is_terminal:
                self.workflow.escalate()

        return result
    def solve(self, domains, evidence=None):
        # Execute, aggregate, attach, and evaluate diagnostics while
        # coordinating the canonical TechnicianWorkflow lifecycle.
        #
        # Eligible remediation is prepared as UNAUTHORIZED.
        # Authorization and execution remain separate boundaries.
        if self.workflow.state is WorkflowState.OPEN:
            self.workflow.start_investigation()

        elif self.workflow.is_terminal:
            raise ValueError(
                "Cannot solve using a terminal TechnicianWorkflow."
            )

        summary = self.execute_domains(
            domains,
            evidence=evidence,
        )

        if not summary["results"]:
            if (
                not self.workflow.is_terminal
                and self.workflow.state is not WorkflowState.ESCALATED
            ):
                self.workflow.escalate()

            return {
                "case": self.case,
                "result": None,
                "domain_results": summary["results"],
                "domain_failures": summary["failures"],
                "state": self.state,
                "workflow_state": self.workflow.state,
            "lifecycle_history": [
                {
                    "from": previous_state.value,
                    "to": new_state.value,
                }
                for previous_state, new_state in self.workflow.history
            ],
                "action_required": False,
                "action_decisions": [],
                "remediation_actions": {},
                "authorizations": {},
            }

        result = self.aggregate_domain_results()

        case = self.attach_diagnostic_result(
            result
        )

        if self.workflow.state is WorkflowState.INVESTIGATING:
            self.workflow.mark_diagnosed()

        action_decision = (
            self.evaluate_action_requirement()
        )

        remediation = {
            "actions": {},
            "authorizations": {},
        }

        if action_decision["action_required"]:
            remediation = (
                self.prepare_remediation_authorization()
            )

        return {
            "case": case,
            "result": result,
            "domain_results": self.domain_results,
            "domain_failures": self.domain_failures,
            "state": self.state,
            "workflow_state": self.workflow.state,
            "lifecycle_history": [
                {
                    "from": previous_state.value,
                    "to": new_state.value,
                }
                for previous_state, new_state in self.workflow.history
            ],
            "action_required": action_decision[
                "action_required"
            ],
            "action_decisions": action_decision[
                "decisions"
            ],
            "remediation_actions": remediation[
                "actions"
            ],
            "authorizations": remediation[
                "authorizations"
            ],
        }

    def attach_diagnostic_result(self, result=None):
        if result is None:
            result = self._result

        if result is None:
            raise ValueError(
                "No diagnostic result is available to attach."
            )

        case = self.coordinator.attach_result(
            self.case,
            result,
        )

        self._state = ProblemSolvingState.DIAGNOSED
        return case

    def set_result(self, result):
        normalized = WindowsDiagnosticResultNormalizer.normalize(
            result
        )
        self._result = deepcopy(normalized)
        return self.result
    def set_state(self, state):
        valid_states = {
            value
            for value in vars(ProblemSolvingState).values()
            if isinstance(value, str) and value.isupper()
        }

        if state not in valid_states:
            raise ValueError(
                f"Invalid problem-solving state: {state}"
            )

        self._state = state
        return self.state

    def fail(self, error):
        if error is None:
            raise ValueError(
                "fail requires a non-null error."
            )

        self._failure = {
            "type": type(error).__name__,
            "message": str(error),
        }
        self._state = ProblemSolvingState.FAILED
        return self.failure

    def _execution_boundary_available(self):
        # Read-only projection helper. It does not execute anything.
        return any(
            self.authorization_allows_execution(action_id)
            and action.operation is not None
            and action.execution_status == "NOT_EXECUTED"
            for action_id, action
            in self._remediation_actions.items()
        )
    @property
    def recovery_cycles(self):
        """Return a defensive copy of the canonical recovery cycles."""
        return list(self.recovery_history.cycles)

    @property
    def current_recovery_cycle(self):
        """Return the current canonical recovery cycle."""
        return self.recovery_history.latest_cycle

    @property
    def recovery_cycle_count(self):
        """Return the number of recorded recovery cycles."""
        return self.recovery_history.cycle_count

    def start_recovery_cycle(self):
        """
        Explicitly begin the next recovery cycle.

        Recovery is deliberately explicit. Failed verification does not
        automatically create a recovery cycle and this method never
        executes remediation or diagnostics by itself.
        """
        if self.workflow.state is not WorkflowState.REMEDIATING:
            raise ValueError(
                "Recovery can only begin while workflow is REMEDIATING."
            )

        # The canonical recovery-cycle contract requires INVESTIGATING.
        # Re-enter investigation through the existing workflow lifecycle.
        self.workflow.start_investigation()

        previous_cycle = self.recovery_history.latest_cycle
        recovery_cycle = previous_cycle.start_recovery_cycle()

        self.recovery_history.record_cycle(recovery_cycle)

        self._state = ProblemSolvingState.PENDING

        return recovery_cycle

    def projection(self):
        return {
            "verification_result": self.verification_result,
            "verification_complete": self.verification_complete,
            "recovery_cycle_count": self.recovery_cycle_count,
            "recovery_cycles": [
                {
                    "cycle_number": cycle.cycle_number,
                    "started_at": cycle.started_at,
                    "is_original": cycle.is_original,
                    "is_recovery": cycle.is_recovery,
                    "outcome": cycle.outcome,
                }
                for cycle in self.recovery_cycles
            ],
            "current_recovery_cycle": {
                "cycle_number": self.current_recovery_cycle.cycle_number,
                "started_at": self.current_recovery_cycle.started_at,
                "is_original": self.current_recovery_cycle.is_original,
                "is_recovery": self.current_recovery_cycle.is_recovery,
                "outcome": self.current_recovery_cycle.outcome,
            },
            "projection_schema_version": self.PROJECTION_SCHEMA_VERSION,
            "case_id": self.case.case_id,
            "machine_id": getattr(self.case, "machine_id", None),
            "state": self.state,
            "workflow_state": self.workflow.state,
            "lifecycle_history": [
                {
                    "from": previous_state.value,
                    "to": new_state.value,
                }
                for previous_state, new_state in self.workflow.history
            ],
            "action_required": (
                self.workflow.state
                is WorkflowState.ACTION_REQUIRED
            ),
            "result": self.result,
            "failure": self.failure,
            "domain_results": self.domain_results,
            "domain_failures": self.domain_failures,
            "remediation_actions": self.remediation_actions,
            "authorizations": self.authorizations,
            "execution_available": self._execution_boundary_available(),
        }

    def architecture_surface(self):
        return {
            "case": self.case,
            "workflow": self.workflow,
            "diagnostic_registry": self.diagnostic_registry,
        }
