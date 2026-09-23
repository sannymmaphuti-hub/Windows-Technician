from engine.rules.base_rule import BaseRule


class NetworkAdapterRule(BaseRule):

    name = "Network Adapter Rule"
    category = "NETWORK"

    def evaluate(self, evidence):

        adapters = evidence.get("adapters")

        if adapters is None:
            return None

        usable_adapters = [
            adapter
            for adapter in adapters
            if adapter.get("ip_address") != "127.0.0.1"
        ]

        if not usable_adapters:

            return {
                "category": "NETWORK",
                "severity": "WARNING",
                "message": "No usable network adapter was detected.",
                "confidence": 0.90
            }

        return None

