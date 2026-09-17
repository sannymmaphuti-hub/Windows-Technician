from engine.diagnostic_action_outcome import DiagnosticActionOutcome
from engine.observation import Observation


class DiagnosticOutcomeToObservation:
    def translate(self, outcome):
        if not isinstance(outcome, DiagnosticActionOutcome):
            raise ValueError(
                "outcome must be a DiagnosticActionOutcome."
            )

        evidence = outcome.evidence

        if "gateway_reachable" in evidence:
            return Observation(
                source="diagnostic_action",
                subject="network_gateway",
                attribute="reachable",
                value=evidence["gateway_reachable"],
            )

        if "dns_working" in evidence:
            return Observation(
                source="diagnostic_action",
                subject="dns",
                attribute="resolution_working",
                value=evidence["dns_working"],
            )

        if "internet_reachable" in evidence:
            return Observation(
                source="diagnostic_action",
                subject="internet",
                attribute="reachable",
                value=evidence["internet_reachable"],
            )

        if "adapters" in evidence:
            return Observation(
                source="diagnostic_action",
                subject="network_adapter",
                attribute="state",
                value=evidence["adapters"],
            )

        raise ValueError(
            "Unsupported diagnostic evidence."
        )