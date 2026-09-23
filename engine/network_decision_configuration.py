from engine.diagnostic_decision_orchestrator import (
    DiagnosticDecisionOrchestrator,
)
from engine.network_adapter_decision_rule import (
    NetworkAdapterDecisionRule,
)
from engine.gateway_reachability_decision_rule import (
    GatewayReachabilityDecisionRule,
)
from engine.dns_resolution_decision_rule import (
    DNSResolutionDecisionRule,
)
from engine.internet_connectivity_decision_rule import (
    InternetConnectivityDecisionRule,
)


def create_network_decision_orchestrator():
    orchestrator = DiagnosticDecisionOrchestrator()

    orchestrator.register_rule(NetworkAdapterDecisionRule())
    orchestrator.register_rule(GatewayReachabilityDecisionRule())
    orchestrator.register_rule(DNSResolutionDecisionRule())
    orchestrator.register_rule(InternetConnectivityDecisionRule())

    return orchestrator
