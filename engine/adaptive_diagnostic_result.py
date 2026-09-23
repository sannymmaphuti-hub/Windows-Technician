class AdaptiveDiagnosticResult:
    VALID_STOP_REASONS = {
        "NO_DECISION",
        "MAX_STEPS",
    }

    _OBSERVATIONS_UNSET = object()

    def __init__(
        self,
        evidence,
        decisions,
        actions,
        steps,
        stopped_reason,
        observations=_OBSERVATIONS_UNSET,
    ):
        if not isinstance(evidence, dict):
            raise ValueError(
                "evidence must be a dictionary."
            )

        if not isinstance(decisions, list):
            raise ValueError(
                "decisions must be a list."
            )

        if not isinstance(actions, list):
            raise ValueError(
                "actions must be a list."
            )

        observations_supplied = (
            observations is not self._OBSERVATIONS_UNSET
        )

        if not observations_supplied:
            observations = []

        if not isinstance(observations, list):
            raise ValueError(
                "observations must be a list."
            )

        if not isinstance(steps, int) or isinstance(steps, bool):
            raise ValueError(
                "steps must be a non-negative integer."
            )

        if steps < 0:
            raise ValueError(
                "steps must be a non-negative integer."
            )

        if stopped_reason not in self.VALID_STOP_REASONS:
            raise ValueError(
                f"stopped_reason must be one of "
                f"{self.VALID_STOP_REASONS}."
            )

        self.evidence = dict(evidence)
        self.decisions = list(decisions)
        self.actions = list(actions)
        self.observations = list(observations)
        self._observations_supplied = observations_supplied
        self.steps = steps
        self.stopped_reason = stopped_reason

    def to_dict(self):
        result = {
            "evidence": dict(self.evidence),
            "decisions": list(self.decisions),
            "actions": list(self.actions),
            "steps": self.steps,
            "stopped_reason": self.stopped_reason,
        }

        if self._observations_supplied:
            result["observations"] = list(self.observations)

        return result
