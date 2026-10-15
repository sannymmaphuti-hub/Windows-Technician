from copy import deepcopy

from engine.fleet import Fleet
from engine.fleet_operational_projection import FleetOperationalProjection


class FleetWorkspace:
    """
    Technician-facing fleet workspace.

    FleetWorkspace composes the canonical FleetOperationalProjection
    into a stable presentation boundary.

    It does not:
    - diagnose
    - reason
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self, fleet, cases=None, alerts=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetWorkspace requires a Fleet."
            )

        self.fleet = fleet
        self.operational_projection = FleetOperationalProjection(
            fleet,
            cases=cases,
            alerts=alerts,
        )

    @property
    def fleet_id(self):
        return self.fleet.fleet_id

    @property
    def fleet_name(self):
        return self.fleet.name

    def machine_inventory(self):
        return deepcopy(
            self.operational_projection.machine_inventory()
        )

    def health(self):
        return deepcopy(
            self.operational_projection.health_projection()
        )

    def cases(self):
        return deepcopy(
            self.operational_projection.case_projection()
        )

    def alerts(self):
        return deepcopy(
            self.operational_projection.alert_projection()
        )

    def workspace_projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet_id,
                "name": self.fleet_name,
            },
            "inventory": self.machine_inventory(),
            "health": self.health(),
            "cases": self.cases(),
            "alerts": self.alerts(),
        }
