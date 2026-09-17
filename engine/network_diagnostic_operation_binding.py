from engine.diagnostic_action_executor import DiagnosticActionExecutor
from diagnostics.network import (
    get_default_gateway,
    get_network_adapters,
    ping_host,
    test_dns_resolution,
    test_internet_connectivity,
)


class NetworkDiagnosticOperationBinding:
    def register(self, executor):
        if not isinstance(executor, DiagnosticActionExecutor):
            raise ValueError(
                "executor must be a DiagnosticActionExecutor."
            )

        executor.register_operation(
            "COLLECT_NETWORK_ADAPTER_STATE",
            self._collect_network_adapter_state,
        )

        executor.register_operation(
            "PING_DEFAULT_GATEWAY",
            self._ping_default_gateway,
        )

        executor.register_operation(
            "TEST_DNS_RESOLUTION",
            self._test_dns_resolution,
        )

        executor.register_operation(
            "TEST_INTERNET_CONNECTIVITY",
            self._test_internet_connectivity,
        )

    def _collect_network_adapter_state(self):
        adapters = get_network_adapters()

        return {
            "adapters": adapters,
        }

    def _ping_default_gateway(self):
        gateway = get_default_gateway()

        if gateway is None:
            return {
                "gateway_reachable": False,
            }

        reachable = ping_host(gateway)

        return {
            "gateway_reachable": reachable,
        }

    def _test_dns_resolution(self):
        working = test_dns_resolution()

        return {
            "dns_working": working,
        }

    def _test_internet_connectivity(self):
        reachable = test_internet_connectivity()

        return {
            "internet_reachable": reachable,
        }