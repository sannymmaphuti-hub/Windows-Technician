from copy import deepcopy

from engine.adaptive_diagnostic_result import (
    AdaptiveDiagnosticResult,
)


class NetworkDiagnosticEvidenceAdapter:
    """
    Converts adaptive diagnostic evidence into the evidence
    contract consumed by the v0.5 network reasoning pipeline.

    This adapter translates evidence only.

    It does not create:
    - findings
    - correlations
    - root causes
    - recommendations
    - remediation decisions
    """

    REQUIRED_ADAPTIVE_RESULT = AdaptiveDiagnosticResult

    def convert(self, adaptive_result):
        if not isinstance(
            adaptive_result,
            self.REQUIRED_ADAPTIVE_RESULT,
        ):
            raise ValueError(
                "adaptive_result must be an "
                "AdaptiveDiagnosticResult."
            )

        source = adaptive_result.evidence

        evidence = deepcopy(source)

        adapters = source.get("adapters")

        if adapters is not None:
            evidence["active_adapter"] = (
                self._select_active_adapter(adapters)
            )

        return evidence

    @staticmethod
    def _select_active_adapter(adapters):
        if not isinstance(adapters, list):
            raise ValueError(
                "adaptive network adapters evidence "
                "must be a list."
            )

        for adapter in adapters:
            if not isinstance(adapter, dict):
                continue

            if not adapter.get("is_up"):
                continue

            if NetworkDiagnosticEvidenceAdapter._has_valid_ipv4(
                adapter
            ):
                return deepcopy(adapter)

        return None

    @staticmethod
    def _has_valid_ipv4(adapter):
        addresses = adapter.get("addresses", [])

        if not isinstance(addresses, list):
            return False

        for address in addresses:
            if not isinstance(address, dict):
                continue

            if address.get("type") != "IPv4":
                continue

            classification = address.get(
                "classification"
            )

            if classification in {
                "PRIVATE",
                "PUBLIC",
            }:
                return True

        return False