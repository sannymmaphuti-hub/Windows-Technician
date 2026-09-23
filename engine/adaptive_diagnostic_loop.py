from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class AdaptiveDiagnosticLoop:
    def __init__(
        self,
        decision_engine,
        action_selector,
        executor,
        max_steps=100,
        observation_translator=None,
    ):
        if not callable(getattr(decision_engine, "decide", None)):
            raise ValueError(
                "decision_engine must provide a callable decide method."
            )

        if not callable(getattr(action_selector, "select", None)):
            raise ValueError(
                "action_selector must provide a callable select method."
            )

        if not callable(getattr(executor, "execute", None)):
            raise ValueError(
                "executor must provide a callable execute method."
            )

        if not isinstance(max_steps, int) or isinstance(max_steps, bool):
            raise ValueError(
                "max_steps must be a positive integer."
            )

        if max_steps <= 0:
            raise ValueError(
                "max_steps must be a positive integer."
            )

        if observation_translator is not None:
            if not callable(
                getattr(observation_translator, "translate", None)
            ):
                raise ValueError(
                    "observation_translator must provide a callable "
                    "translate method."
                )

        self.decision_engine = decision_engine
        self.action_selector = action_selector
        self.executor = executor
        self.max_steps = max_steps
        self.observation_translator = observation_translator

    def run(self, evidence):
        if not isinstance(evidence, dict):
            raise ValueError(
                "evidence must be a dictionary."
            )

        current_evidence = dict(evidence)
        decisions = []
        actions = []
        observations = []
        steps = 0

        while steps < self.max_steps:
            current_decisions = self.decision_engine.decide(
                current_evidence
            )

            if not current_decisions:
                return AdaptiveDiagnosticResult(
                    evidence=current_evidence,
                    decisions=decisions,
                    actions=actions,
                    steps=steps,
                    stopped_reason="NO_DECISION",
                    observations=observations,
                )

            decision = current_decisions[0]

            decision_type = getattr(
                decision,
                "decision_type",
                decision,
            )

            decisions.append(decision_type)

            action = self.action_selector.select(
                decision_type
            )

            if action is None:
                raise ValueError(
                    f"No diagnostic action selected for decision: "
                    f"{decision_type}."
                )

            actions.append(action.action_type)

            outcome = self.executor.execute(action)

            if not isinstance(outcome, DiagnosticActionOutcome):
                raise ValueError(
                    "diagnostic executor must return a DiagnosticActionOutcome."
                )

            if self.observation_translator is not None:
                observation = self.observation_translator.translate(
                    outcome
                )
                observations.append(observation)

            current_evidence.update(outcome.evidence)
            steps += 1

        return AdaptiveDiagnosticResult(
            evidence=current_evidence,
            decisions=decisions,
            actions=actions,
            steps=steps,
            stopped_reason="MAX_STEPS",
            observations=observations,
        )
