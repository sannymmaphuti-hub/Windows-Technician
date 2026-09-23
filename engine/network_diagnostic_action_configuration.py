from engine.diagnostic_action_selection_orchestrator import (
    DiagnosticActionSelectionOrchestrator,
)
from engine.network_adapter_diagnostic_action_rule import (
    NetworkAdapterDiagnosticActionRule,
)
from engine.gateway_diagnostic_action_rule import (
    GatewayDiagnosticActionRule,
)
from engine.dns_diagnostic_action_rule import (
    DNSDiagnosticActionRule,
)
from engine.internet_diagnostic_action_rule import (
    InternetDiagnosticActionRule,
)


def create_network_diagnostic_action_orchestrator():
    orchestrator = DiagnosticActionSelectionOrchestrator()

    orchestrator.register_rule(
        NetworkAdapterDiagnosticActionRule()
    )
    orchestrator.register_rule(
        GatewayDiagnosticActionRule()
    )
    orchestrator.register_rule(
        DNSDiagnosticActionRule()
    )
    orchestrator.register_rule(
        InternetDiagnosticActionRule()
    )

    return orchestrator
