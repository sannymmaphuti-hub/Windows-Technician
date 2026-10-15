from copy import deepcopy

from engine.fleet import Fleet
from engine.fleet_alert_aggregation import FleetAlertAggregation
from engine.fleet_case_aggregation import FleetCaseAggregation
from engine.fleet_health_aggregation import FleetHealthAggregation
from engine.fleet_machine_inventory import FleetMachineInventory


class FleetOperationalProjection:
    """
    Canonical technician-facing fleet operational projection.

    Composes existing fleet inventory, health, case, and alert
    boundaries into one read-only operational surface.

    This class does not:
    - diagnose
    - reason
    - create findings
    - create root causes
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    - mutate fleet state
    """

    def __init__(self, fleet, cases=None, alerts=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetOperationalProjection requires a Fleet."
            )

        self.fleet = fleet
        self.inventory = FleetMachineInventory(fleet)
        self.health = FleetHealthAggregation(fleet)
        self.cases = FleetCaseAggregation(fleet, cases)
        self.alerts = FleetAlertAggregation(fleet, alerts)

    def machine_inventory(self):
        return deepcopy(self.inventory.inventory_projection())

    def health_projection(self):
        return deepcopy(self.health.projection())

    def case_projection(self):
        return deepcopy(self.cases.projection())

    def alert_projection(self):
        return deepcopy(self.alerts.projection())

    def projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
            },
            "inventory": self.machine_inventory(),
            "health": self.health_projection(),
            "cases": self.case_projection(),
            "alerts": self.alert_projection(),
        }
