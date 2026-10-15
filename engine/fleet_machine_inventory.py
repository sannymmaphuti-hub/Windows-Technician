from copy import deepcopy

from engine.fleet import Fleet


class FleetMachineInventory:
    """
    Technician-facing fleet machine inventory projection.

    FleetMachineInventory reads the canonical Fleet membership and
    ManagedMachine state. It does not create, mutate, diagnose,
    authorize, remediate, or verify machines.
    """

    def __init__(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetMachineInventory requires a Fleet."
            )

        self.fleet = fleet

    @property
    def machine_count(self):
        return self.fleet.machine_count

    def machines(self):
        return deepcopy(
            [
                self._machine_snapshot(machine)
                for machine in self.fleet.machines
            ]
        )

    def get_machine(self, machine_id):
        machine = self.fleet.get_machine(machine_id)

        if machine is None:
            return None

        return deepcopy(
            self._machine_snapshot(machine)
        )

    def connected_machines(self):
        return deepcopy(
            [
                self._machine_snapshot(machine)
                for machine in self.fleet.connected_machines
            ]
        )

    def disconnected_machines(self):
        return deepcopy(
            [
                self._machine_snapshot(machine)
                for machine in self.fleet.disconnected_machines
            ]
        )

    def healthy_machines(self):
        return deepcopy(
            [
                self._machine_snapshot(machine)
                for machine in self.fleet.healthy_machines
            ]
        )

    def warning_machines(self):
        return deepcopy(
            [
                self._machine_snapshot(machine)
                for machine in self.fleet.warning_machines
            ]
        )

    def inventory_projection(self):
        return {
            "fleet": {
                "fleet_id": self.fleet.fleet_id,
                "name": self.fleet.name,
                "machine_count": self.machine_count,
            },
            "machines": self.machines(),
        }

    @staticmethod
    def _machine_snapshot(machine):
        return {
            "machine_id": machine.machine_id,
            "hostname": machine.hostname,
            "platform": machine.platform,
            "operating_system": machine.operating_system,
            "connection_state": machine.connection_state,
            "health_state": machine.health_state,
            "last_seen": machine.last_seen,
        }
