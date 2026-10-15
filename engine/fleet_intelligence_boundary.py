from copy import deepcopy

from engine.fleet import Fleet
from engine.fleet_alert_aggregation import FleetAlertAggregation
from engine.fleet_case_aggregation import FleetCaseAggregation
from engine.fleet_health_aggregation import FleetHealthAggregation
from engine.fleet_machine_inventory import FleetMachineInventory


class FleetIntelligenceBoundary:
    """
    V1.0 canonical fleet-intelligence boundary.

    Composes the existing fleet inventory, health, case, and alert
    intelligence surfaces into one stable input boundary.

    This boundary does not:
    - diagnose machines
    - execute remediation
    - authorize remediation
    - verify remediation
    - mutate fleet state
    - create a second fleet lifecycle
    """

    def __init__(self, fleet, cases=None, alerts=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetIntelligenceBoundary requires a Fleet."
            )

        self.fleet = fleet
        self.inventory = FleetMachineInventory(fleet)
        self.health = FleetHealthAggregation(fleet)
        self.cases = FleetCaseAggregation(fleet, cases)
        self.alerts = FleetAlertAggregation(fleet, alerts)

    def inventory_projection(self):
        return deepcopy(
            self.inventory.inventory_projection()
        )

    def health_projection(self):
        return deepcopy(
            self.health.projection()
        )

    def case_projection(self):
        return deepcopy(
            self.cases.projection()
        )

    def alert_projection(self):
        return deepcopy(
            self.alerts.projection()
        )

    def projection(self):
        """
        Return the canonical read-only fleet intelligence input.
        """
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "inventory": self.inventory_projection(),
            "health": self.health_projection(),
            "cases": self.case_projection(),
            "alerts": self.alert_projection(),
        }
